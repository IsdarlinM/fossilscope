from __future__ import annotations

import sys

from . import cli_evolution as _cli_evolution  # noqa: F401
from .cli_vnext import app

__all__ = ["app", "normalize_help_argv", "run"]


def normalize_help_argv(argv: list[str]) -> list[str]:
    """Normalize trailing `help` for root and nested FossilScope commands."""
    normalized = list(argv)
    if len(normalized) >= 3 and normalized[-1] == "help" and normalized[1] != "help":
        normalized[-1] = "--help"
    return normalized


def run() -> None:
    """Console entrypoint including every public FossilScope command."""
    sys.argv[:] = normalize_help_argv(sys.argv)
    app()
