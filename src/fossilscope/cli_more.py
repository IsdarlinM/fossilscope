from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import typer
from sric.workspace import Workspace
from sric.evidence import EvidenceStore
from sric.models import Provenance, ProvenanceType
from sric.plugins import PluginRegistry
from sric.scope import ScopeEngine, ScopePolicy
from sric.updater import perform_update
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import NotebookEntry, ResearchNotebook
from . import __version__
from .api import create_app
from .core import FossilEngine
from .models import Observation
from .cli import app, root_default, wp

@app.command("lifecycle")
def lifecycle_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Show candidate fossil lifecycle without equating historical evidence to current exposure."""
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).lifecycle(), indent=2))


@app.command("graph-at")
def graph_at_command(
    workspace: str,
    at: Optional[str] = typer.Option(None, "--at", help="ISO-8601 timestamp for time-travel graph."),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Render the temporal graph at a supplied point in time."""
    when = datetime.fromisoformat(at) if at else None
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).temporal_graph(when), indent=2, default=str))


@app.command("api-diff")
def api_diff_command(
    workspace: str,
    before: Path = typer.Argument(..., exists=True, dir_okay=False),
    after: Path = typer.Argument(..., exists=True, dir_okay=False),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Compare supplied historical/current API specifications passively."""
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).historical_api_diff(before, after), indent=2))


@app.command("confidence")
def confidence_command(
    workspace: str, value: str, stale_after_days: int = typer.Option(365, "--stale-after-days", min=1), root: Path = typer.Option(root_default(), "--root")
) -> None:
    """Explain confidence decay for evidence that has not been re-observed."""
    try:
        payload = FossilEngine(wp(workspace, root)).confidence_decay(value, stale_after_days)
    except KeyError:
        typer.echo("Observation value not found", err=True)
        raise typer.Exit(2)
    typer.echo(json.dumps(payload, indent=2))


@app.command("clusters")
def clusters_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Group supplied observations by explicit lineage/acquisition/issuer hints."""
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).clusters(), indent=2))


@app.command("acquisitions")
def acquisitions_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """Show explicit acquisition/brand lineage relationships with evidence/confidence."""
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).acquisition_lineage(), indent=2))

@app.command()
def report(
    workspace: str, output: Path, root: Path = typer.Option(root_default(), "--root")
) -> None:
    e = FossilEngine(wp(workspace, root))
    c = e.score()
    output.write_text(
        "# FossilScope Report\n\n## Facts\nHistorical and current observations are separated.\n\n## Candidates\n```json\n"
        + json.dumps([x.model_dump(mode="json") for x in c], indent=2)
        + "\n```\n\nCandidates are hypotheses unless explicitly validated with deterministic evidence.\n",
        encoding="utf-8",
    )
    typer.echo(str(output))


@app.command()
def demo(workspace: str = "demo", root: Path = typer.Option(root_default(), "--root")) -> None:
    path = wp(workspace, root)
    if not path.exists():
        root.mkdir(parents=True, exist_ok=True)
        Workspace.create(root, workspace)
    e = FossilEngine(path)
    e.add_observation(
        Observation(
            observation_id="o1",
            entity_type="api_endpoint",
            value="https://api-v1.example.test/export",
            source="archive",
            first_seen=datetime(2021, 1, 1),
            last_seen=datetime(2022, 6, 1),
            auth_relevance=True,
            evidence_ids=["E1"],
        )
    )
    e.add_observation(
        Observation(
            observation_id="o2",
            entity_type="api_endpoint",
            value="https://api-v1.example.test/export",
            source="sdk",
            current_reference=True,
            current_reachable=True,
            evidence_ids=["E2"],
        )
    )
    typer.echo(json.dumps([x.model_dump(mode="json") for x in e.score()], indent=2))


@app.command()
def web(
    workspace: str,
    host: str = "127.0.0.1",
    port: int = 8767,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        typer.echo(
            "Non-loopback binding disabled until authenticated TLS mode is configured.", err=True
        )
        raise typer.Exit(4)
    import uvicorn

    uvicorn.run(create_app(wp(workspace, root)), host=host, port=port)


@app.command("evidence")
def evidence_add(
    workspace: str,
    file: Path,
    source: str = typer.Option("user", "--source"),
    media_type: str = typer.Option("application/octet-stream", "--media-type"),
    redacted: bool = typer.Option(False, "--redacted"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Store a local evidence artifact in SRIC content-addressed storage."""
    if not file.is_file():
        typer.echo("evidence input must be a regular file", err=True)
        raise typer.Exit(2)
    workspace_path = wp(workspace, root)
    Workspace.open(workspace_path)
    store = EvidenceStore(workspace_path / "evidence")
    ref = store.put_bytes(
        file.read_bytes(),
        media_type=media_type,
        provenance=Provenance(
            provenance_type=ProvenanceType.USER_INPUT,
            source=source,
            method="cli_evidence_add",
            tool_version=__version__,
        ),
        redacted=redacted,
    )
    typer.echo(json.dumps(ref.model_dump(mode="json"), indent=2))


@app.command("ai")
def ai_status() -> None:
    """Show AI mode. Cloud AI remains disabled until explicitly configured."""
    typer.echo(
        json.dumps({"mode": "disabled", "provider": "disabled", "cloud_uploads": False}, indent=2)
    )


@app.command("plugins")
def plugins_list(path: Path = typer.Option(Path.home() / ".sric" / "plugins", "--path")) -> None:
    """List SRIC plugin manifests without auto-executing plugin code."""
    for manifest in PluginRegistry(path).list():
        typer.echo(f"{manifest.name}\t{manifest.version}\t{manifest.type}")


@app.command("scope")
def scope_check(
    target: str,
    method: str = typer.Option("GET", "--method"),
    allow: list[str] = typer.Option([], "--allow"),
    deny: list[str] = typer.Option([], "--deny"),
) -> None:
    """Evaluate a target using SRIC Scope Engine; no request is sent."""
    decision = ScopeEngine(
        ScopePolicy(allow_targets=allow, deny_targets=deny, allowed_methods={method.upper()})
    ).evaluate(target, method)
    typer.echo(
        json.dumps(
            {
                "allowed": decision.allowed,
                "reason": decision.reason,
                "matched_rule": decision.matched_rule,
            },
            indent=2,
        )
    )
    if not decision.allowed:
        raise typer.Exit(3)




@app.command("query")
def shared_query(
    workspace: str, query: str, limit: int = typer.Option(50, "--limit", min=1, max=500), root: Path = typer.Option(root_default(), "--root")
) -> None:
    """Search this workspace's shared SRIC graph."""
    typer.echo(json.dumps(TemporalGraph(wp(workspace, root)).search(query, limit), indent=2, default=str))


@app.command("notebook")
def notebook_command(
    workspace: str,
    entry_type: str | None = typer.Option(None, "--type"),
    title: str | None = typer.Option(None, "--title"),
    body: str | None = typer.Option(None, "--body"),
    status: str = typer.Option("OBSERVED", "--status"),
    save_query_name: str | None = typer.Option(None, "--save-query-name"),
    query: str | None = typer.Option(None, "--query"),
    list_queries: bool = typer.Option(False, "--list-queries"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """List/append research notes or manage saved investigation queries."""
    notebook = ResearchNotebook(wp(workspace, root))
    if save_query_name or query:
        if not (save_query_name and query):
            raise typer.BadParameter("--save-query-name and --query are required together")
        notebook.save_query(save_query_name, query)
        typer.echo(json.dumps({"saved": save_query_name, "query": query}, indent=2))
        return
    if list_queries:
        typer.echo(json.dumps(notebook.saved_queries(), indent=2))
        return
    if entry_type or title or body:
        if not (entry_type and title and body):
            raise typer.BadParameter("--type, --title and --body are required together")
        typer.echo(notebook.add(NotebookEntry(entry_type=entry_type, title=title, body=body, status=status)).model_dump_json(indent=2))
        return
    typer.echo(json.dumps([x.model_dump(mode="json") for x in notebook.list()], indent=2, default=str))


@app.command("evidence-lineage")
def evidence_lineage_command(
    workspace: str, artifact_id: str, root: Path = typer.Option(root_default(), "--root")
) -> None:
    """Explain evidence lineage and the reason a derived artifact is visible."""
    try:
        payload = EvidenceLineage(wp(workspace, root)).explain(artifact_id)
    except KeyError:
        typer.echo(f"Unknown lineage artifact: {artifact_id}", err=True)
        raise typer.Exit(2)
    typer.echo(json.dumps(payload, indent=2, default=str))


@app.command("jobs")
def jobs_command(
    workspace: str, job_id: Optional[str] = typer.Option(None, "--id"), cancel: bool = typer.Option(False, "--cancel"), root: Path = typer.Option(root_default(), "--root")
) -> None:
    """List/inspect/cancel persistent SRIC jobs for this workspace."""
    engine = JobEngine(wp(workspace, root))
    if job_id and cancel:
        typer.echo(engine.request_cancel(job_id).model_dump_json(indent=2))
        return
    if job_id:
        typer.echo(
            json.dumps(
                {
                    "job": engine.get(job_id).model_dump(mode="json"),
                    "events": [x.model_dump(mode="json") for x in engine.events(job_id)],
                },
                indent=2,
                default=str,
            )
        )
        return
    typer.echo(json.dumps([x.model_dump(mode="json") for x in engine.list()], indent=2, default=str))

@app.command("update")
def update(
    check: bool = typer.Option(False, "--check"),
    manifest: Optional[str] = typer.Option(None, "--manifest"),
    public_key: Optional[Path] = typer.Option(None, "--public-key"),
) -> None:
    """Check/install a signed wheel release. Never performs a blind git pull."""
    import os

    source = manifest or os.getenv("FOSSILSCOPE_RELEASE_MANIFEST_URL")
    key = public_key or (
        Path(os.environ["FOSSILSCOPE_RELEASE_PUBLIC_KEY"])
        if os.getenv("FOSSILSCOPE_RELEASE_PUBLIC_KEY")
        else None
    )
    if not source or key is None:
        typer.echo(
            "No trusted release channel configured. Provide --manifest and --public-key.", err=True
        )
        raise typer.Exit(2)
    try:
        status = perform_update(
            manifest_source=source,
            public_key_path=key,
            expected_product="fossilscope",
            current_version=__version__,
            check_only=check,
        )
    except Exception as exc:
        typer.echo(f"Update verification failed; no update was installed: {exc}", err=True)
        raise typer.Exit(6)
    typer.echo(json.dumps(status.__dict__, indent=2))


@app.command("help", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def help_command(ctx: typer.Context, command: Optional[str] = typer.Argument(None)) -> None:
    if not command:
        typer.echo(ctx.parent.get_help() if ctx.parent else ctx.get_help())
        return
    root = ctx.parent.command if ctx.parent else app
    if hasattr(root, "commands") and command in root.commands:
        typer.echo(root.commands[command].get_help(ctx))
        return
    raise typer.Exit(2)

