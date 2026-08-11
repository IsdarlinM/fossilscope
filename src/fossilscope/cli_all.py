from __future__ import annotations

import typer
from sric.cli_style import CLIBrand, configure_cli_context, no_color_option, run_branded_cli

from . import __version__
from . import cli_evolution as _cli_evolution  # noqa: F401
from . import cli_planning as _cli_planning  # noqa: F401
from .cli_vnext import app
from . import cli_capabilities as _cli_capabilities  # noqa: F401
from . import cli_update as _cli_update  # noqa: F401,E402

__all__ = ["BRAND", "app", "normalize_help_argv", "run"]

BRAND = CLIBrand(
    product="FossilScope",
    description="Map historical attack surface and separate history from current exposure.",
    version=__version__,
)
app.rich_markup_mode = None


@app.callback(invoke_without_command=True)
def branded_main(
    ctx: typer.Context,
    no_color: bool = no_color_option(),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        is_eager=True,
        help="Show the FossilScope version and exit.",
    ),
) -> None:
    """FossilScope CLI presentation controls."""

    if version:
        typer.echo(__version__)
        raise typer.Exit()
    configure_cli_context(ctx, no_color=no_color)


def normalize_help_argv(argv: list[str]) -> list[str]:
    """Normalize trailing `help` for root and nested FossilScope commands."""
    normalized = list(argv)
    if len(normalized) >= 3 and normalized[-1] == "help":
        normalized[-1] = "--help"
    return normalized


def run() -> None:
    """Console entrypoint including the branded CLI and local Web/API."""

    run_branded_cli(app, BRAND, argv_normalizer=normalize_help_argv)
