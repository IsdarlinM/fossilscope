from __future__ import annotations

from . import cli_evolution as _cli_evolution  # noqa: F401
from .cli_vnext import app, run as _run

__all__ = ["app", "run"]


def run() -> None:
    _run()
