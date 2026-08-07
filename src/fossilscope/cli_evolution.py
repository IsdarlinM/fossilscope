from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli_vnext import app
from .evolution import (
    VersionedArtifactObservation,
    diff_artifact_versions,
    find_stale_references,
)


def _read_observations(path: Path) -> list[VersionedArtifactObservation]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise typer.BadParameter("artifact observations JSON must be a list")
    try:
        return [VersionedArtifactObservation.model_validate(item) for item in raw]
    except ValidationError as exc:
        typer.echo(f"invalid artifact observation: {exc}", err=True)
        raise typer.Exit(2) from exc


@app.command("evolution-diff")
def evolution_diff(path: Path) -> None:
    """Compare passive API, OAuth, SDK and documentation artifact versions."""
    try:
        reports = diff_artifact_versions(_read_observations(path))
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in reports],
            indent=2,
            default=str,
        )
    )


@app.command("stale-references")
def stale_references(path: Path) -> None:
    """Find current references to values removed from historical artifacts."""
    observations = _read_observations(path)
    try:
        reports = find_stale_references(observations)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in reports],
            indent=2,
            default=str,
        )
    )
