from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import typer
from sric.workspace import Workspace
from sric.plugins import PluginRegistry
from . import __version__
from .core import FossilEngine
from .models import Observation

app = typer.Typer(
    name="fossilscope",
    help="Attack Surface Archaeology + Temporal Security Graph.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    rich_markup_mode=None,
)


def root_default() -> Path:
    return Path.home() / ".fossilscope" / "workspaces"


def wp(name: str, root: Path) -> Path:
    return root / name


@app.command()
def version() -> None:
    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check runtime, SRIC integration, plugin registry and secure defaults."""
    import sric

    plugin_path = Path.home() / ".sric" / "plugins"
    plugins = PluginRegistry(plugin_path).list()
    checks: dict[str, dict[str, object]] = {
        "python": {"ok": sys.version_info >= (3, 11), "version": sys.version.split()[0]},
        "sric": {"ok": sric.__version__.startswith("0.3."), "version": sric.__version__},
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {"ok": True, "count": len(plugins), "path": str(plugin_path)},
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(item["ok"]) for item in checks.values())
    typer.echo(json.dumps({"ok": ok, "checks": checks}, indent=2))
    if not ok:
        raise typer.Exit(1)


@app.command()
def init(name: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    root.mkdir(parents=True, exist_ok=True)
    ws = Workspace.create(root, name)
    FossilEngine(ws.root)
    typer.echo(str(ws.root))


@app.command("workspace")
def workspace_command(
    action: str = typer.Argument("list", help="create|list|show|archive"),
    name: Optional[str] = typer.Argument(None),
    root: Path = typer.Option(root_default(), "--root"),
    confirm: bool = typer.Option(False, "--confirm", help="Required for archive."),
) -> None:
    """Manage isolated investigation workspaces."""
    root.mkdir(parents=True, exist_ok=True)
    action = action.lower()
    if action == "list":
        items = sorted(
            p.name for p in root.iterdir() if p.is_dir() and (p / "workspace.json").is_file()
        )
        typer.echo(json.dumps({"workspaces": items}, indent=2))
        return
    if not name:
        typer.echo(f"workspace {action} requires NAME", err=True)
        raise typer.Exit(2)
    target = wp(name, root)
    if action == "create":
        ws = Workspace.create(root, name)
        FossilEngine(ws.root)
        typer.echo(str(ws.root))
        return
    if action == "show":
        ws = Workspace.open(target)
        meta = json.loads((ws.root / "workspace.json").read_text(encoding="utf-8"))
        typer.echo(json.dumps({"path": str(ws.root), "metadata": meta}, indent=2))
        return
    if action == "archive":
        if not confirm:
            typer.echo("workspace archive requires --confirm; no data was changed", err=True)
            raise typer.Exit(5)
        Workspace.open(target)
        archive_root = root / "archived"
        archive_root.mkdir(exist_ok=True)
        destination = archive_root / name
        if destination.exists():
            typer.echo("archive destination already exists; no data was changed", err=True)
            raise typer.Exit(2)
        target.rename(destination)
        typer.echo(str(destination))
        return
    typer.echo(f"Unknown workspace action: {action}", err=True)
    raise typer.Exit(2)


@app.command("config")
def config_command(
    action: str = typer.Argument("show", help="show|explain"),
    key: Optional[str] = typer.Argument(None),
    workspace: Optional[str] = typer.Option(None, "--workspace"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Inspect configuration and explain where a value comes from."""
    defaults: dict[str, object] = {"telemetry": False, "cloud_ai": False, "external_uploads": False}
    values = dict(defaults)
    sources = {k: "secure default" for k in values}
    if workspace:
        meta_path = wp(workspace, root) / "workspace.json"
        if not meta_path.is_file():
            typer.echo("workspace.json not found", err=True)
            raise typer.Exit(2)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for k in values:
            if k in meta:
                values[k] = meta[k]
                sources[k] = f"workspace config: {meta_path}"
    if action == "show":
        typer.echo(json.dumps({"values": values, "sources": sources}, indent=2))
        return
    if action == "explain":
        if not key or key not in values:
            typer.echo("config explain requires one of: " + ", ".join(sorted(values)), err=True)
            raise typer.Exit(2)
        typer.echo(json.dumps({"key": key, "value": values[key], "source": sources[key]}, indent=2))
        return
    typer.echo(f"Unknown config action: {action}", err=True)
    raise typer.Exit(2)


@app.command()
def add(
    workspace: str,
    observation_id: str,
    entity_type: str,
    value: str,
    source: str,
    first_seen: Optional[datetime] = None,
    last_seen: Optional[datetime] = None,
    current_reachable: Optional[bool] = None,
    auth_relevance: bool = False,
    sensitivity_hint: bool = False,
    current_reference: bool = False,
    evidence: list[str] = typer.Option([], "--evidence"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    FossilEngine(wp(workspace, root)).add_observation(
        Observation(
            observation_id=observation_id,
            entity_type=entity_type,
            value=value,
            source=source,
            first_seen=first_seen,
            last_seen=last_seen,
            current_reachable=current_reachable,
            auth_relevance=auth_relevance,
            sensitivity_hint=sensitivity_hint,
            current_reference=current_reference,
            evidence_ids=evidence,
        )
    )
    typer.echo(observation_id)


@app.command("import")
def import_cmd(
    workspace: str, path: Path, root: Path = typer.Option(root_default(), "--root")
) -> None:
    typer.echo(str(FossilEngine(wp(workspace, root)).import_json(path)))


@app.command()
def collect(
    workspace: str | None = None,
    adapter: str | None = None,
    path: Path | None = None,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Normalize an explicit passive-source export; never performs hidden crawling."""
    if workspace is None and adapter is None and path is None:
        typer.echo("PASSIVE mode: no unbounded active crawling. Adapters = ct,dns,repo,package,openapi,js,sourcemap,docs,archive,securitytxt,sitemap; supply WORKSPACE ADAPTER PATH to ingest an explicit local export.")
        return
    if not workspace or not adapter or path is None:
        raise typer.BadParameter("WORKSPACE, ADAPTER and PATH must be supplied together")
    count = FossilEngine(wp(workspace, root)).collect_adapter(path, adapter)
    typer.echo(json.dumps({"mode": "PASSIVE", "adapter": adapter, "imported": count}, indent=2))


@app.command()
def extract(
    workspace: str,
    path: Path,
    source: str = typer.Option("local_artifact", "--source"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Passively extract endpoint/domain references from a local text artifact."""
    typer.echo(str(FossilEngine(wp(workspace, root)).extract_artifact(path, source)))


@app.command()
def timeline(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).timeline(), indent=2))


@app.command()
def diff(
    workspace: str,
    before: datetime,
    after: datetime,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).diff(before, after), indent=2))


@app.command()
def fossils(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    typer.echo(
        json.dumps(
            [x.model_dump(mode="json") for x in FossilEngine(wp(workspace, root)).score()], indent=2
        )
    )


@app.command()
def correlate(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    typer.echo(json.dumps(FossilEngine(wp(workspace, root)).correlate(), indent=2))


@app.command()
def validate(
    workspace: str,
    candidate_id: str,
    evidence: list[str] = typer.Option([], "--evidence"),
    confirm: bool = False,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    if not confirm or not evidence:
        typer.echo(
            "Validation requires --confirm and deterministic evidence; active probing is not automatic.",
            err=True,
        )
        raise typer.Exit(5)
    data = FossilEngine(wp(workspace, root)).store.load()
    found = False
    for c in data["candidates"]:
        if c["candidate_id"] == candidate_id:
            c["status"] = "VALIDATED"
            c["evidence_ids"] = sorted(set(c.get("evidence_ids", []) + evidence))
            found = True
    if not found:
        raise typer.Exit(2)
    FossilEngine(wp(workspace, root)).store.save(data)
    typer.echo(candidate_id)


@app.command("export")
def export_cmd(
    workspace: str,
    output: Path,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    output.write_text(
        json.dumps(FossilEngine(wp(workspace, root)).store.load(), indent=2), encoding="utf-8"
    )
    typer.echo(str(output))





# Register extended command surface without duplicating the root Typer app.
from . import cli_more as _cli_more  # noqa: F401,E402

def run() -> None:
    if len(sys.argv) >= 3 and sys.argv[-1] == "help":
        sys.argv[-1] = "--help"
    app()
