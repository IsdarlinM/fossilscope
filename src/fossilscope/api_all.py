from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sric.capabilities import discover_capabilities

from . import __version__
from .api_vnext import create_app as create_base_app
from .sric_bootstrap import status as sric_runtime_status


API_DOCS_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FossilScope API</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#0d110e;color:#edf0e8}
body{margin:0}main{max-width:1100px;margin:auto;padding:24px}.muted{color:#9fac9e}
.endpoint{border:1px solid #354035;border-radius:10px;padding:12px;margin:10px 0;background:#151b15}
.method{font:700 12px ui-monospace,monospace;margin-right:8px;color:#b8e8c2}code{overflow-wrap:anywhere}
</style>
</head>
<body><main><h1>FossilScope Local API</h1><p class="muted">Offline OpenAPI explorer. Schema source: <a href="/openapi.json">/openapi.json</a>.</p><div id="status">Loading API schema…</div><div id="paths"></div></main><script src="/assets/api-docs.js"></script></body>
</html>"""

API_DOCS_JS = """(()=>{const status=document.getElementById('status');const root=document.getElementById('paths');fetch('/openapi.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('OpenAPI HTTP '+r.status);return r.json()}).then(spec=>{status.textContent=(spec.info?.title||'API')+' · '+(spec.info?.version||'');const paths=spec.paths||{};Object.keys(paths).sort().forEach(path=>{Object.entries(paths[path]).forEach(([method,op])=>{if(!['get','post','put','patch','delete','options','head'].includes(method))return;const card=document.createElement('section');card.className='endpoint';const heading=document.createElement('div');const m=document.createElement('span');m.className='method';m.textContent=method.toUpperCase();const code=document.createElement('code');code.textContent=path;heading.append(m,code);card.append(heading);const text=document.createElement('p');text.className='muted';text.textContent=op.summary||op.description||'No description provided.';card.append(text);root.append(card)})})}).catch(err=>{status.textContent='Unable to load API schema: '+err.message})})();"""


def _mount_degraded_workbench(app: FastAPI, reason: str) -> None:
    @app.get("/workbench", include_in_schema=False)
    async def workbench_unavailable() -> HTMLResponse:
        return HTMLResponse(
            "<h1>Sentinel Forge runtime repair required</h1>"
            "<p>The native FossilScope temporal dashboard remains available, but the shared "
            "Security Workspace cannot start because SRIC Core is incompatible.</p>"
            f"<pre>{reason}</pre><p>Run <code>fossilscope doctor</code> and "
            "<code>fossilscope update</code>, or rerun the installer.</p>",
            status_code=503,
        )

    @app.get("/api/v1/workbench/coverage", include_in_schema=False)
    async def workbench_coverage_unavailable() -> JSONResponse:
        return JSONResponse(
            {
                "complete": False,
                "status": "RUNTIME_INCOMPATIBLE",
                "reason": reason,
                "repair": "fossilscope update or rerun installer",
            },
            status_code=503,
        )


def _replace_external_docs(app: FastAPI) -> None:
    app.router.routes = [
        route
        for route in app.router.routes
        if getattr(route, "path", None) != "/docs"
    ]

    @app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
    async def local_api_docs() -> str:
        return API_DOCS_HTML

    @app.get("/assets/api-docs.js", include_in_schema=False)
    async def local_api_docs_js() -> Response:
        return Response(API_DOCS_JS, media_type="application/javascript")


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)
    _replace_external_docs(app)

    @app.exception_handler(ValueError)
    async def invalid_value(_request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "INVALID_INPUT",
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(KeyError)
    async def missing_research_entity(_request: Request, exc: KeyError) -> JSONResponse:
        raw = exc.args[0] if exc.args else "requested research entity"
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"No matching research entity was found: {raw}",
                }
            },
        )

    @app.get("/api/v1/capabilities", tags=["standalone"])
    async def capabilities() -> dict[str, object]:
        return discover_capabilities(current_product="fossilscope").model_dump(mode="json")

    @app.get("/api/v1/runtime-compatibility", tags=["standalone"])
    async def runtime_compatibility() -> dict[str, object]:
        runtime = sric_runtime_status()
        return {
            "compatible": runtime.compatible,
            "sric_version": runtime.version,
            "missing_modules": list(runtime.missing_modules),
            "reasons": list(runtime.reasons),
        }

    try:
        from sric.web_catalog import install_json_safe_catalog
        from sric.web_console import WebConsoleConfig, mount_web_console

        install_json_safe_catalog()
    except ModuleNotFoundError as exc:
        _mount_degraded_workbench(
            app,
            f"missing shared Web console/catalog module: {exc.name or exc}",
        )
        return app

    config = WebConsoleConfig(
        product="fossilscope",
        display_name="FossilScope",
        cli_module="fossilscope.cli_all",
        version=__version__,
    )
    manager = mount_web_console(app, config)
    try:
        from sric.web_security_workspace import mount_security_workspace
    except ModuleNotFoundError as exc:
        _mount_degraded_workbench(
            app,
            f"missing shared Security Workspace module: {exc.name or exc}",
        )
    else:
        mount_security_workspace(app, config, manager)
    return app
