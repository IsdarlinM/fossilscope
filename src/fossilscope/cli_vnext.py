from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import typer
from sric.plugins import PluginRegistry
from sric.scope import ScopeEngine, ScopePolicy
from sric.workspace import Workspace

from . import cli as base
from .advanced import FossilIntelligence
from .collector_runtime import PassiveHTTPSCollectorRuntime
from .core import FossilEngine
from .lifecycle import SurfaceEvidence, assess_lifecycle
from .reobservation import ReobservationRequest, deduplicate_requests, evaluate_reobservation, schedule_retry
from .sric_bootstrap import status as sric_runtime_status

app = base.app
wp = base.wp
root_default = base.root_default


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


@app.command("doctor")
def doctor_vnext(
    json_output: bool = typer.Option(False, "--json"),
    plugin_path: Path = typer.Option(root_default() / "plugins", "--plugin-path"),
) -> None:
    """Check Python, exact SRIC feature compatibility, plugins and privacy."""
    plugins = PluginRegistry(plugin_path).list()
    runtime = sric_runtime_status()
    checks = {
        "python": {"ok": sys.version_info >= (3, 11), "version": sys.version.split()[0]},
        "sric": {
            "ok": runtime.compatible,
            "version": runtime.version,
            "required": ">=0.5.16,<0.6",
            "missing_modules": list(runtime.missing_modules),
            "reasons": list(runtime.reasons),
        },
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {"ok": True, "count": len(plugins)},
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(value["ok"]) for value in checks.values())
    if json_output:
        typer.echo(json.dumps({"ok": ok, "checks": checks}, indent=2))
    else:
        typer.echo("\n".join(f"[{'OK' if value['ok'] else 'FAIL'}] {name}: {value}" for name, value in checks.items()))
    if not ok:
        raise typer.Exit(1)


@app.command("collect-url")
def collect_url(
    workspace: str,
    url: str,
    adapter: str,
    allow: list[str] = typer.Option([], "--allow"),
    ack_terms: bool = typer.Option(False, "--ack-terms"),
    cache_ttl: int = typer.Option(3600, "--cache-ttl", min=0),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Perform a bounded HTTPS GET through Scope/Policy and import observations."""
    if not allow:
        typer.echo("collect-url requires at least one --allow target; no request was sent", err=True)
        raise typer.Exit(3)
    workspace_path = wp(workspace, root)
    Workspace.open(workspace_path)
    runtime = PassiveHTTPSCollectorRuntime(workspace_path / "fossilscope" / "collector-cache", ScopeEngine(ScopePolicy(allow_targets=allow, allowed_methods={"GET"})), ttl_seconds=cache_ttl)
    try:
        result = runtime.collect(url, adapter, ack_terms=ack_terms)
    except (PermissionError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(3) from exc
    engine = FossilEngine(workspace_path)
    for observation in result.observations:
        engine.add_observation(observation)
    typer.echo(json.dumps({"mode": "PASSIVE_GET_ONLY", "url": result.url, "cache_hit": result.cache_hit, "sha256": result.sha256, "size_bytes": result.size_bytes, "imported": len(result.observations), "provenance": result.provenance}, indent=2))


@app.command("time-travel")
def time_travel(workspace: str, at: str = typer.Option(..., "--at"), root: Path = typer.Option(root_default(), "--root")) -> None:
    """Reconstruct the temporal graph at an ISO-8601 instant."""
    try:
        when = datetime.fromisoformat(at.replace("Z", "+00:00"))
    except ValueError as exc:
        typer.echo("--at must be ISO-8601", err=True)
        raise typer.Exit(2) from exc
    output = FossilIntelligence(FossilEngine(wp(workspace, root))).time_travel(when)
    typer.echo(json.dumps(output, indent=2, default=str))


@app.command("resurrections")
def resurrections(workspace: str, min_gap_days: int = typer.Option(180, "--min-gap-days", min=1), root: Path = typer.Option(root_default(), "--root")) -> None:
    """List resurrection hypotheses; historical evidence never proves current exposure."""
    output = FossilIntelligence(FossilEngine(wp(workspace, root))).resurrection_candidates(min_gap_days=min_gap_days)
    typer.echo(json.dumps(output, indent=2, default=str))


@app.command("confidence-v2")
def confidence_v2(workspace: str, value: str, stale_after_days: int = typer.Option(365, "--stale-after-days", min=1), root: Path = typer.Option(root_default(), "--root")) -> None:
    """Explain historical/current confidence and temporal decay."""
    try:
        payload = FossilIntelligence(FossilEngine(wp(workspace, root))).confidence_v2(value, stale_after_days)
    except KeyError as exc:
        typer.echo("Observation value not found", err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(payload, indent=2, default=str))


@app.command("mobile-archaeology")
def mobile_archaeology(workspace: str, old_artifact: Path, new_artifact: Path, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Compare two local mobile artifacts without executing them."""
    if not old_artifact.is_file() or not new_artifact.is_file():
        typer.echo("Both artifacts must be regular files", err=True)
        raise typer.Exit(2)
    output = FossilIntelligence(FossilEngine(wp(workspace, root))).mobile_api_archaeology(old_artifact, new_artifact)
    typer.echo(json.dumps(output, indent=2, default=str))


@app.command("lifecycle-assess")
def lifecycle_assess(path: Path) -> None:
    """Classify current exposure lifecycle from evidence-bearing JSON records."""
    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("surface evidence JSON must be a list")
    evidence = [SurfaceEvidence.model_validate(item) for item in raw]
    output = assess_lifecycle(evidence)
    typer.echo(json.dumps([item.model_dump(mode="json") for item in output], indent=2, default=str))


@app.command("reobserve-plan")
def reobserve_plan(path: Path, deduplicate: bool = typer.Option(True, "--deduplicate/--keep-duplicates")) -> None:
    """Evaluate passive/active reobservation requests without executing them."""
    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("reobservation requests JSON must be a list")
    requests = [ReobservationRequest.model_validate(item) for item in raw]
    if deduplicate:
        requests = deduplicate_requests(requests)
    output = [evaluate_reobservation(item) for item in requests]
    typer.echo(json.dumps([item.model_dump(mode="json") for item in output], indent=2, default=str))
    if any(not item.executable for item in output):
        raise typer.Exit(2)


@app.command("reobserve-retry")
def reobserve_retry(path: Path, base_delay_seconds: int = typer.Option(60, "--base-delay", min=1), maximum_delay_seconds: int = typer.Option(86400, "--max-delay", min=1)) -> None:
    """Create a bounded exponential-backoff retry record; no request is sent."""
    raw = _read_json(path)
    if not isinstance(raw, dict):
        raise typer.BadParameter("reobservation request JSON must be an object")
    request = ReobservationRequest.model_validate(raw)
    updated = schedule_retry(request, base_delay_seconds=base_delay_seconds, maximum_delay_seconds=maximum_delay_seconds)
    typer.echo(updated.model_dump_json(indent=2))


def run() -> None:
    base.run()
