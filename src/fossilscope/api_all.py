from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sric.capabilities import discover_capabilities
from sric.web_theme import SENTINEL_THEME_TOKENS_CSS

from . import __version__
from .api_vnext import create_app as create_base_app
from .sric_bootstrap import status as sric_runtime_status


API_DOCS_CSS = r"""
.forge-shell{min-height:100vh;display:grid;grid-template-columns:236px minmax(0,1fr)}
.global-rail{position:sticky;top:0;height:100vh;display:flex;flex-direction:column;gap:26px;padding:24px 18px;background:var(--rail);border-right:1px solid var(--line-soft)}
.brand-lockup{display:flex;align-items:center;gap:11px}.brand-mark{width:38px;height:38px;display:grid;place-items:center;border:1px solid #36515b;border-radius:10px;background:#102128;color:#91d1dc;font-weight:800;letter-spacing:.04em}.brand-name{margin:0;font-size:.9rem;font-weight:720}.brand-caption{margin:3px 0 0;color:var(--muted);font-size:.69rem;line-height:1.35}
.rail-label,.section-kicker,.status-label{display:block;color:var(--muted);font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.095em}.product-lockup{display:grid;gap:5px;padding:14px;border:1px solid var(--line-soft);border-radius:var(--radius-md);background:#111820}.product-version{color:#a6b5c2;font-size:.74rem}.rail-nav{display:grid;gap:6px}.rail-link{display:flex;align-items:center;min-height:38px;padding:0 11px;border-radius:var(--radius-sm);color:#9eadba;text-decoration:none;font-size:.82rem}.rail-link:hover{background:#141f29;color:var(--text)}.rail-link.active{background:#17252d;color:#d9eef1;box-shadow:inset 2px 0 0 var(--accent)}.rail-principle{margin-top:auto;padding:14px;border-top:1px solid var(--line-soft);display:grid;gap:4px;color:var(--text-soft);font-size:.78rem}.rail-principle strong{margin-top:4px;color:#d8e4eb}
.workspace-shell{width:min(1600px,100%);margin:0 auto;padding:30px clamp(18px,3vw,42px) 42px}.workspace-header{display:flex;justify-content:space-between;align-items:flex-start;gap:30px;margin-bottom:20px}.eyebrow{margin:0 0 8px;color:#7fb5bf;font-size:.7rem;font-weight:750;text-transform:uppercase;letter-spacing:.11em}.workspace-header h1{margin:0;font-size:clamp(1.8rem,3vw,2.7rem);line-height:1.05;letter-spacing:-.025em;font-weight:680}.workspace-subtitle{max-width:800px;margin:10px 0 0;color:var(--muted);line-height:1.55;font-size:.9rem}.workspace-status{min-width:220px;display:grid;gap:5px;padding:13px 15px;border:1px solid var(--line);border-radius:var(--radius-md);background:var(--surface)}.workspace-status strong{font-size:.8rem;color:#bcd3d8}.status-count{color:var(--muted);font-size:.72rem}
.docs-guardrail{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:13px 16px;margin-bottom:18px;border:1px solid #29434b;border-radius:var(--radius-md);background:#101c22}.docs-guardrail strong{font-size:.84rem}.docs-guardrail p{max-width:760px;margin:0;color:#91a5af;font-size:.78rem;line-height:1.45;text-align:right}.docs-guardrail a{color:#a8d8e0}
.toolbar{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px;align-items:end;margin-bottom:16px}.search-wrap{position:relative}.search-wrap span{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:#667888}.search-wrap input{width:100%;border:1px solid #344252;border-radius:var(--radius-sm);background:#0d131a;color:var(--text);padding:10px 11px 10px 33px}.filters{display:flex;gap:6px;overflow-x:auto;max-width:650px}.chip{white-space:nowrap;border:1px solid #303d4c;background:#111820;color:#94a4b2;border-radius:999px;padding:7px 10px;font-size:.7rem;font-weight:650;cursor:pointer}.chip.active{background:var(--accent-soft);border-color:#3e6f79;color:#b8e0e6}
.docs-grid{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:16px;align-items:start}.panel{min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-lg);box-shadow:0 10px 28px rgba(0,0,0,.16);overflow:hidden}.section-head{padding:16px 18px 14px;border-bottom:1px solid var(--line-soft)}.section-head h2{margin:5px 0 0;font-size:1rem}.section-head p{margin:7px 0 0;color:var(--muted);font-size:.78rem;line-height:1.45}.endpoint-list{padding:7px 14px 15px}.endpoint{margin-top:9px;border:1px solid var(--line-soft);border-radius:var(--radius-md);background:var(--surface-3);overflow:hidden}.endpoint summary{list-style:none;cursor:pointer;padding:14px}.endpoint summary::-webkit-details-marker{display:none}.endpoint-summary{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:11px;align-items:center}.method{min-width:52px;text-align:center;border-radius:6px;padding:5px 7px;background:#132b31;border:1px solid #31545d;color:#a9dae2;font:750 .68rem var(--font-mono)}.method.post{background:#282216;border-color:#574a2d;color:#e0bf86}.method.delete{background:#2b1919;border-color:#603838;color:#e2a3a0}.path{overflow-wrap:anywhere;color:#dce7ed;font:600 .81rem var(--font-mono)}.tag{color:var(--muted);font-size:.68rem}.endpoint-title{margin:7px 0 0;color:#b9c5cf;font-size:.78rem}.endpoint-body{padding:0 14px 15px;border-top:1px solid var(--line-soft)}.description{color:#a8b5c0;font-size:.8rem;line-height:1.55}.subhead{margin:16px 0 8px;color:#d7e1e7;font-size:.76rem;text-transform:uppercase;letter-spacing:.07em}.kv{display:grid;grid-template-columns:minmax(100px,160px) 1fr;gap:10px;padding:9px 0;border-bottom:1px solid #1c2631}.kv:last-child{border-bottom:0}.kv code,.schema-code{font:12px/1.5 var(--font-mono)}.kv small{display:block;color:var(--muted);margin-top:3px;line-height:1.45}.required{color:#d7a467}.location{color:#7193a5}.schema-box{border:1px solid var(--line-soft);border-radius:8px;background:#0a1016;padding:10px;overflow:auto}.schema-code{white-space:pre-wrap;word-break:break-word;color:#b9cad5;margin:0}.response-code{color:#8ec5a3;font:750 .75rem var(--font-mono)}
.models-panel{position:sticky;top:18px}.models-list{max-height:calc(100vh - 210px);overflow:auto;padding:8px 14px 16px}.model{border-bottom:1px solid var(--line-soft);padding:10px 2px}.model:last-child{border-bottom:0}.model summary{cursor:pointer;color:#dbe5eb;font:650 .78rem var(--font-mono)}.model pre{white-space:pre-wrap;word-break:break-word;color:#9fb0bd;font:11px/1.5 var(--font-mono);margin:9px 0 0}.empty{padding:20px;color:var(--muted);font-size:.82rem}
@media(max-width:1050px){.docs-grid{grid-template-columns:1fr}.models-panel{position:static}.models-list{max-height:none}.toolbar{grid-template-columns:1fr}.filters{max-width:100%}}
@media(max-width:780px){.forge-shell{display:block}.global-rail{position:static;height:auto;padding:14px;gap:14px}.brand-caption,.rail-principle{display:none}.product-lockup{padding:10px 12px}.rail-nav{grid-template-columns:repeat(3,1fr)}.rail-link{justify-content:center;text-align:center}.workspace-shell{padding:20px 14px 34px}.workspace-header,.docs-guardrail{align-items:stretch;flex-direction:column}.workspace-status{min-width:0}.docs-guardrail p{text-align:left}.endpoint-summary{grid-template-columns:auto minmax(0,1fr)}.tag{grid-column:2}}
"""

API_DOCS_HTML = (
    """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FossilScope API Reference · Sentinel Forge</title><style>"""
    + SENTINEL_THEME_TOKENS_CSS
    + API_DOCS_CSS
    + """</style></head><body><div class='forge-shell'><aside class='global-rail' aria-label='Sentinel Forge navigation'><div class='brand-lockup'><span class='brand-mark' aria-hidden='true'>SF</span><div><p class='brand-name'>Sentinel Forge</p><p class='brand-caption'>Evidence-native security research</p></div></div><div class='product-lockup'><span class='rail-label'>Active product</span><strong>FossilScope</strong><span class='product-version'>v__VERSION__</span></div><nav class='rail-nav'><a class='rail-link' href='/'>Dashboard</a><a class='rail-link' href='/workbench'>Security Workspace</a><span class='rail-link active' aria-current='page'>API Reference</span></nav><div class='rail-principle' role='note'><span class='rail-label'>Control principle</span><strong>AI proposes.</strong><span>Evidence proves.</span><span>Humans control.</span></div></aside><div class='workspace-shell'><header class='workspace-header'><div><p class='eyebrow'>Local Developer Interface</p><h1>API Reference</h1><p class='workspace-subtitle'>Offline OpenAPI reference for FossilScope temporal research, analysis and shared SRIC runtime endpoints. Documentation describes what each operation proves—and what it does not.</p></div><div class='workspace-status'><span class='status-label'>OpenAPI contract</span><strong id='status'>Loading schema…</strong><span id='endpoint-count' class='status-count'></span></div></header><section class='docs-guardrail'><strong>Reference-only explorer: no request execution controls are exposed.</strong><p>The schema is served locally from <a href='/openapi.json'>/openapi.json</a>. POST analysis endpoints compute plans or analysis; documentation never sends them automatically.</p></section><div class='toolbar'><div class='search-wrap'><span aria-hidden='true'>⌕</span><input id='search' type='search' placeholder='Search paths, summaries, tags or descriptions' aria-label='Search API reference'></div><div id='tag-filters' class='filters' aria-label='API tag filters'></div></div><main class='docs-grid'><section class='panel'><div class='section-head'><span class='section-kicker'>Operations</span><h2>Endpoints</h2><p>Expand an endpoint to inspect parameters, request bodies, response contracts and evidence semantics.</p></div><div id='paths' class='endpoint-list'></div></section><aside class='panel models-panel'><div class='section-head'><span class='section-kicker'>Schemas</span><h2>Data models</h2><p>OpenAPI component schemas used by request and response contracts.</p></div><div id='models' class='models-list'></div></aside></main></div></div><script src='/assets/api-docs.js'></script></body></html>"""
)

API_DOCS_JS = r"""(()=>{'use strict';const status=document.getElementById('status'),count=document.getElementById('endpoint-count'),root=document.getElementById('paths'),models=document.getElementById('models'),search=document.getElementById('search'),filters=document.getElementById('tag-filters');let records=[],active='all';const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n};const schemaText=s=>JSON.stringify(s??{},null,2);function schemaLabel(s){if(!s)return'any';if(s.$ref)return s.$ref.split('/').pop();if(s.type==='array')return'array<'+schemaLabel(s.items)+'>';return s.type||s.oneOf?.map(schemaLabel).join(' | ')||s.anyOf?.map(schemaLabel).join(' | ')||'object'}function addSchema(parent,schema){const box=el('div','schema-box'),pre=el('pre','schema-code',schemaText(schema));box.append(pre);parent.append(box)}function renderParams(body,params){if(!params?.length)return;body.append(el('h4','subhead','Parameters'));params.forEach(p=>{const row=el('div','kv'),left=el('div'),right=el('div');left.append(el('code','',p.name));const meta=el('small');meta.append(document.createTextNode((p.in||'parameter')+' · '+schemaLabel(p.schema)));if(p.required)meta.append(el('span','required',' · required'));left.append(meta);right.append(el('div','',p.description||'No description provided.'));if(p.schema?.default!==undefined)right.append(el('small','',`Default: ${JSON.stringify(p.schema.default)}`));if(p.example!==undefined)right.append(el('small','',`Example: ${JSON.stringify(p.example)}`));row.append(left,right);body.append(row)})}function renderBody(body,requestBody){if(!requestBody)return;body.append(el('h4','subhead','Request body'));if(requestBody.description)body.append(el('p','description',requestBody.description));const content=requestBody.content||{};Object.entries(content).forEach(([type,media])=>{const line=el('div','kv'),left=el('div'),right=el('div');left.append(el('code','',type));if(requestBody.required)left.append(el('small','required','required'));right.append(el('div','',`Schema: ${schemaLabel(media.schema)}`));if(media.example!==undefined)right.append(el('small','',`Example: ${JSON.stringify(media.example)}`));line.append(left,right);body.append(line);addSchema(body,media.schema)})}function renderResponses(body,responses){if(!responses)return;body.append(el('h4','subhead','Responses'));Object.entries(responses).forEach(([code,r])=>{const row=el('div','kv'),left=el('div'),right=el('div');left.append(el('span','response-code',code));right.append(el('div','',r.description||'Response'));const content=r.content||{};Object.entries(content).forEach(([type,media])=>right.append(el('small','',`${type} · ${schemaLabel(media.schema)}`)));row.append(left,right);body.append(row)})}function card(rec){const d=document.createElement('details');d.className='endpoint';d.dataset.search=rec.search;d.dataset.tags=rec.tags.join(',');const s=document.createElement('summary'),line=el('div','endpoint-summary'),m=el('span','method '+rec.method,rec.method.toUpperCase()),p=el('code','path',rec.path),tag=el('span','tag',rec.tags.join(' · ')||'untagged');line.append(m,p,tag);s.append(line,el('p','endpoint-title',rec.op.summary||'No summary provided.'));d.append(s);const body=el('div','endpoint-body');if(rec.op.description)body.append(el('p','description',rec.op.description));renderParams(body,rec.op.parameters);renderBody(body,rec.op.requestBody);renderResponses(body,rec.op.responses);d.append(body);return d}function apply(){const q=search.value.trim().toLowerCase();root.replaceChildren();let visible=0;records.forEach(r=>{if(active!=='all'&&!r.tags.includes(active))return;if(q&&!r.search.includes(q))return;root.append(card(r));visible++});if(!visible)root.append(el('p','empty','No API operations match the current filter.'));count.textContent=`${visible} of ${records.length} operations`}function renderFilters(tags){filters.replaceChildren();['all',...tags].forEach(tag=>{const b=el('button','chip'+(tag===active?' active':''),tag==='all'?'All':tag);b.type='button';b.onclick=()=>{active=tag;renderFilters(tags);apply()};filters.append(b)})}function renderModels(spec){models.replaceChildren();const schemas=spec.components?.schemas||{};const names=Object.keys(schemas).sort();names.forEach(name=>{const d=document.createElement('details');d.className='model';const s=document.createElement('summary');s.textContent=name;const pre=document.createElement('pre');pre.textContent=schemaText(schemas[name]);d.append(s,pre);models.append(d)});if(!names.length)models.append(el('p','empty','No component schemas published.'))}fetch('/openapi.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('OpenAPI HTTP '+r.status);return r.json()}).then(spec=>{status.textContent=(spec.info?.title||'API')+' · '+(spec.info?.version||'');const tagSet=new Set();Object.keys(spec.paths||{}).sort().forEach(path=>Object.entries(spec.paths[path]).forEach(([method,op])=>{if(!['get','post','put','patch','delete','options','head'].includes(method))return;const tags=op.tags||[];tags.forEach(t=>tagSet.add(t));records.push({path,method,op,tags,search:[path,method,op.summary,op.description,...tags].filter(Boolean).join(' ').toLowerCase()})}));renderFilters([...tagSet].sort());renderModels(spec);apply()}).catch(err=>{status.textContent='Unable to load schema';root.replaceChildren(el('p','empty','Unable to load API schema: '+err.message))});search.addEventListener('input',apply)})();"""


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
        route for route in app.router.routes if getattr(route, "path", None) != "/docs"
    ]

    @app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
    async def local_api_docs() -> str:
        return API_DOCS_HTML.replace("__VERSION__", __version__)

    @app.get("/assets/api-docs.js", include_in_schema=False)
    async def local_api_docs_js() -> Response:
        return Response(
            API_DOCS_JS,
            media_type="application/javascript",
            headers={"Cache-Control": "no-store"},
        )


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)
    _replace_external_docs(app)

    @app.exception_handler(ValueError)
    async def invalid_value(_request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "INVALID_INPUT", "message": str(exc)}},
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

    @app.get(
        "/api/v1/capabilities",
        tags=["standalone"],
        summary="Discover Sentinel Forge capabilities",
        description=(
            "Return the standalone capability contract visible to FossilScope. Sibling products "
            "remain optional integrations rather than hidden runtime dependencies."
        ),
        response_description="Installed and compatible Sentinel Forge capability metadata.",
    )
    async def capabilities() -> dict[str, object]:
        return discover_capabilities(current_product="fossilscope").model_dump(mode="json")

    @app.get(
        "/api/v1/runtime-compatibility",
        tags=["standalone"],
        summary="Check shared SRIC runtime compatibility",
        description="Report the installed SRIC Core version, required shared modules and compatibility reasons used before mounting the Security Workspace.",
    )
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
            app, f"missing shared Web console/catalog module: {exc.name or exc}"
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
            app, f"missing shared Security Workspace module: {exc.name or exc}"
        )
    else:
        mount_security_workspace(app, config, manager)
    return app
