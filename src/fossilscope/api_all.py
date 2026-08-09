from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from sric.capabilities import discover_capabilities
from sric.web_console import WebConsoleConfig, mount_web_console

from . import __version__
from .api_vnext import create_app as create_base_app


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)

    @app.get("/api/v1/capabilities", tags=["standalone"])
    async def capabilities() -> dict[str, object]:
        return discover_capabilities(current_product="fossilscope").model_dump(mode="json")

    mount_web_console(
        app,
        WebConsoleConfig(
            product="fossilscope",
            display_name="FossilScope",
            cli_module="fossilscope.cli_all",
            version=__version__,
        ),
    )
    return app
