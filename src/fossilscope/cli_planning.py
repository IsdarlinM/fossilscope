from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli_vnext import app
from .planning import ReobservationCandidate, plan_reobservation


@app.command("reobservation-priority")
def reobservation_priority(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    maximum_requests: int = typer.Option(50, "--max-requests", min=1, max=1000),
) -> None:
    """Prioritize passive evidence refresh without proving current exposure."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        raw = payload if isinstance(payload, list) else payload.get("candidates", [])
        if not isinstance(raw, list):
            raise ValueError("input must be a JSON list or an object containing candidates")
        candidates = [ReobservationCandidate.model_validate(item) for item in raw]
        requests = plan_reobservation(candidates, maximum_requests=maximum_requests)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        typer.echo(f"re-observation planning failed: {exc}", err=True)
        raise typer.Exit(2) from exc

    typer.echo(
        json.dumps(
            {
                "requests": [item.model_dump(mode="json") for item in requests],
                "planned_request_count": len(requests),
                "passive_only": True,
                "executed": False,
                "requests_sent": 0,
                "validated_findings_created": 0,
            },
            indent=2,
        )
    )
