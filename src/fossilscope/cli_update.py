from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer
from sric.updater import perform_product_update

from . import __version__
from .cli_vnext import app
from .sric_bootstrap import ensure_for_official_update
from .windows_update import stage_official_windows_update


@app.command("update")
def update(
    check: bool = typer.Option(False, "--check", help="Check the official release channel only."),
    force: bool = typer.Option(
        False,
        "--force",
        help="Reinstall the official release even when that same version is already installed. Never downgrades.",
    ),
    manifest: Optional[str] = typer.Option(
        None,
        "--manifest",
        help="Advanced override: custom signed release manifest path or HTTPS URL.",
    ),
    public_key: Optional[Path] = typer.Option(
        None,
        "--public-key",
        help="Advanced override: trusted Ed25519 key for a custom manifest.",
    ),
) -> None:
    """Check/install FossilScope and keep its shared SRIC runtime compatible."""
    if check and force:
        typer.echo("--check and --force cannot be used together.", err=True)
        raise typer.Exit(2)
    custom_requested = bool(
        manifest
        or public_key
        or os.getenv("FOSSILSCOPE_RELEASE_MANIFEST_URL")
        or os.getenv("FOSSILSCOPE_RELEASE_PUBLIC_KEY")
    )
    try:
        if not check and not custom_requested:
            ensure_for_official_update()

        if os.name == "nt" and not check and not custom_requested:
            payload = stage_official_windows_update(
                current_version=__version__,
                force=force,
            )
            typer.echo(json.dumps(payload, indent=2))
            if payload.get("staged"):
                typer.echo(
                    "Windows update staged and cryptographically verified. "
                    "It will be applied after this FossilScope process exits; "
                    f"final status: {payload.get('result_file')}."
                )
            return

        status = perform_product_update(
            expected_product="fossilscope",
            current_version=__version__,
            check_only=check,
            force=force,
            manifest_source=manifest,
            public_key_path=public_key,
            manifest_env="FOSSILSCOPE_RELEASE_MANIFEST_URL",
            public_key_env="FOSSILSCOPE_RELEASE_PUBLIC_KEY",
        )
    except Exception as exc:
        typer.echo(
            f"Update verification failed; no product update was installed: {exc}",
            err=True,
        )
        raise typer.Exit(6)
    typer.echo(json.dumps(status.__dict__, indent=2))
