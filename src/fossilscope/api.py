from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import ResearchNotebook
from sric.web_theme import SENTINEL_THEME_TOKENS_CSS
from sric.workspace import Workspace

from . import __version__
from .advanced import FossilIntelligence
from .core import FossilEngine


OPENAPI_TAGS = [
    {
        "name": "temporal-research",
        "description": "Read-only views over historical observations, lifecycle state, temporal graph and fossil candidates.",
    },
    {
        "name": "intelligence",
        "description": "Explainable temporal analysis. Historical evidence is never promoted to current exposure without current evidence.",
    },
    {
        "name": "research-runtime",
        "description": "Shared SRIC search, jobs, notebook and evidence-lineage endpoints for the local workspace.",
    },
]

DASHBOARD_CSS = r"""
.forge-shell{min-height:100vh;display:grid;grid-template-columns:236px minmax(0,1fr)}
.global-rail{position:sticky;top:0;height:100vh;display:flex;flex-direction:column;gap:26px;padding:24px 18px;background:var(--rail);border-right:1px solid var(--line-soft)}
.brand-lockup{display:flex;align-items:center;gap:11px}.brand-mark{width:38px;height:38px;display:grid;place-items:center;border:1px solid #36515b;border-radius:10px;background:#102128;color:#91d1dc;font-weight:800;letter-spacing:.04em}
.brand-name{margin:0;font-size:.9rem;font-weight:720;letter-spacing:.01em}.brand-caption{margin:3px 0 0;color:var(--muted);font-size:.69rem;line-height:1.35}
.rail-label,.section-kicker,.status-label,.guardrail-kicker{display:block;color:var(--muted);font-size:.67rem;font-weight:700;text-transform:uppercase;letter-spacing:.095em}
.product-lockup{display:grid;gap:5px;padding:14px;border:1px solid var(--line-soft);border-radius:var(--radius-md);background:#111820}.product-lockup strong{font-size:1rem}.product-version{width:fit-content;color:#a6b5c2;font-size:.74rem}
.rail-nav{display:grid;gap:6px}.rail-link{display:flex;align-items:center;min-height:38px;padding:0 11px;border-radius:var(--radius-sm);color:#9eadba;text-decoration:none;font-size:.82rem}.rail-link:hover{background:#141f29;color:var(--text)}.rail-link.active{background:#17252d;color:#d9eef1;box-shadow:inset 2px 0 0 var(--accent)}
.rail-principle{margin-top:auto;padding:14px;border-top:1px solid var(--line-soft);display:grid;gap:4px;color:var(--text-soft);font-size:.78rem}.rail-principle strong{margin-top:4px;color:#d8e4eb}
.workspace-shell{width:min(1600px,100%);margin:0 auto;padding:30px clamp(18px,3vw,42px) 42px}.workspace-header{display:flex;justify-content:space-between;align-items:flex-start;gap:30px;margin-bottom:20px}.eyebrow{margin:0 0 8px;color:#7fb5bf;font-size:.7rem;font-weight:750;text-transform:uppercase;letter-spacing:.11em}.workspace-header h1{margin:0;font-size:clamp(1.8rem,3vw,2.7rem);line-height:1.05;letter-spacing:-.025em;font-weight:680}.workspace-subtitle{max-width:760px;margin:10px 0 0;color:var(--muted);line-height:1.55;font-size:.9rem}
.workspace-status{min-width:210px;display:grid;gap:5px;padding:13px 15px;border:1px solid var(--line);border-radius:var(--radius-md);background:var(--surface)}.workspace-status strong{font-size:.8rem;color:#bcd3d8}.status-count{color:var(--muted);font-size:.72rem}
.guardrail{display:flex;align-items:center;justify-content:space-between;gap:26px;padding:13px 16px;margin-bottom:18px;border:1px solid #29434b;border-radius:var(--radius-md);background:#101c22}.guardrail strong{display:block;margin-top:4px;color:#dbe8eb;font-size:.84rem}.guardrail p{margin:0;max-width:700px;color:#91a5af;font-size:.78rem;line-height:1.45;text-align:right}
.toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:0 0 16px}.toolbar-copy h2{margin:0;font-size:1rem}.toolbar-copy p{margin:5px 0 0;color:var(--muted);font-size:.8rem}.search{display:flex;gap:8px;width:min(460px,100%)}input{width:100%;border:1px solid #344252;border-radius:var(--radius-sm);background:#0d131a;color:var(--text);padding:10px 11px}input::placeholder{color:#5f6e7d}button{border:1px solid #3e6f79;border-radius:var(--radius-sm);background:var(--accent-soft);color:#c7e8ed;padding:9px 13px;font-weight:700;cursor:pointer}button:hover{background:#18363e}.secondary{border-color:var(--line);background:#111820;color:var(--text-soft)}
.dashboard-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.panel{min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-lg);box-shadow:0 10px 28px rgba(0,0,0,.16);overflow:hidden}.panel-head{padding:16px 17px 13px;border-bottom:1px solid var(--line-soft)}.panel-head h3{margin:5px 0 0;font-size:1rem}.panel-head p{margin:7px 0 0;color:var(--muted);font-size:.78rem;line-height:1.45}.panel-body{padding:6px 16px 16px;min-height:260px}
.row{padding:12px 4px;border-bottom:1px solid var(--line-soft);cursor:pointer;line-height:1.45}.row:last-child{border-bottom:0}.row:hover{background:#141f29}.row b{font-weight:650}.muted{color:var(--muted)}.score{font-variant-numeric:tabular-nums;font-weight:750;color:#9fd3dc}
.empty{margin:16px 0;color:var(--muted);font-size:.82rem}.drawer{position:fixed;right:0;top:0;height:100%;width:min(520px,94vw);background:var(--surface);border-left:1px solid var(--line);padding:22px;display:none;overflow:auto;z-index:40;box-shadow:-18px 0 48px rgba(0,0,0,.28)}.drawer.open{display:block}.drawer-header{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:18px}.drawer h3{margin:5px 0 0}.drawer pre{white-space:pre-wrap;word-break:break-word;background:#0a1016;border:1px solid var(--line-soft);border-radius:var(--radius-md);padding:14px;color:#c8d7e1;font:12px/1.55 var(--font-mono)}
@media(max-width:1050px){.dashboard-grid{grid-template-columns:1fr 1fr}.dashboard-grid .panel:last-child{grid-column:1/-1}}
@media(max-width:780px){.forge-shell{display:block}.global-rail{position:static;height:auto;padding:14px;gap:14px}.brand-caption,.rail-principle{display:none}.product-lockup{padding:10px 12px}.rail-nav{grid-template-columns:repeat(3,1fr)}.rail-link{justify-content:center;text-align:center}.workspace-shell{padding:20px 14px 34px}.workspace-header,.guardrail,.toolbar{align-items:stretch;flex-direction:column}.workspace-status{min-width:0}.guardrail p{text-align:left}.search{width:100%}.dashboard-grid{grid-template-columns:1fr}.dashboard-grid .panel:last-child{grid-column:auto}}
"""

HTML = (
    """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FossilScope · Sentinel Forge</title><style>"""
    + SENTINEL_THEME_TOKENS_CSS
    + DASHBOARD_CSS
    + """</style></head><body><div class='forge-shell'><aside class='global-rail' aria-label='Sentinel Forge navigation'><div class='brand-lockup'><span class='brand-mark' aria-hidden='true'>SF</span><div><p class='brand-name'>Sentinel Forge</p><p class='brand-caption'>Evidence-native security research</p></div></div><div class='product-lockup'><span class='rail-label'>Active product</span><strong>FossilScope</strong><span class='product-version'>v__VERSION__ · PASSIVE</span></div><nav class='rail-nav' aria-label='Product navigation'><span class='rail-link active' aria-current='page'>Dashboard</span><a class='rail-link' href='/workbench'>Security Workspace</a><a class='rail-link' href='/docs'>API Reference</a></nav><div class='rail-principle' role='note'><span class='rail-label'>Control principle</span><strong>AI proposes.</strong><span>Evidence proves.</span><span>Humans control.</span></div></aside><div class='workspace-shell'><header class='workspace-header'><div><p class='eyebrow'>Temporal Security Intelligence</p><h1>FossilScope Dashboard</h1><p class='workspace-subtitle'>Investigate historical attack-surface evidence, lifecycle transitions and fossil candidates without confusing historical observations with current exposure.</p></div><div class='workspace-status'><span class='status-label'>Runtime activity</span><strong id='jobStatus'>Jobs: idle</strong><span class='status-count'>Passive-first local workspace</span></div></header><section class='guardrail'><div><span class='guardrail-kicker'>Evidence guardrail</span><strong>Historical evidence never proves current exposure by itself.</strong></div><p>Current reachability requires current evidence. Candidate scores explain prioritization and never represent vulnerability severity.</p></section><section class='toolbar'><div class='toolbar-copy'><h2>Temporal research workspace</h2><p>Select an observation to inspect its evidence and explainability context.</p></div><div class='search'><input id='search' placeholder='Search timeline, candidates or lifecycle' aria-label='Search temporal research data'><button id='searchBtn'>Search</button></div></section><main class='dashboard-grid'><section class='panel'><div class='panel-head'><span class='section-kicker'>Historical observations</span><h3>Temporal Security Graph</h3><p>Chronological evidence remains separate from present-day reachability.</p></div><div class='panel-body' id='timeline'></div></section><section class='panel'><div class='panel-head'><span class='section-kicker'>Research prioritization</span><h3>Fossil Candidates</h3><p>Explainable candidate confidence and status; never vulnerability severity.</p></div><div class='panel-body' id='candidates'></div></section><section class='panel'><div class='panel-head'><span class='section-kicker'>Exposure state</span><h3>Lifecycle</h3><p>Observed lifecycle states with evidence-aware temporal context.</p></div><div class='panel-body' id='lifecycle'></div></section></main></div></div><aside id='drawer' class='drawer' aria-label='Evidence and explainability details'><div class='drawer-header'><div><span class='section-kicker'>Evidence context</span><h3>Evidence / Explainability</h3></div><button id='closeDrawer' class='secondary'>Close</button></div><pre id='drawerBody'></pre></aside><script src='/assets/app.js'></script></body></html>"""
)

JS = r"""function e(v){return String(v??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}function row(v,html){return '<div class="row" tabindex="0" data-x=\''+encodeURIComponent(JSON.stringify(v))+'\'>'+html+'</div>'}function empty(label){return '<p class="empty">'+e(label)+'</p>'}async function json(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error(url+' HTTP '+r.status);return r.json()}async function load(){const [t,c,l]=await Promise.all([json('/api/timeline'),json('/api/candidates'),json('/api/lifecycle')]);document.getElementById('timeline').innerHTML=t.slice(-20).reverse().map(x=>row(x,'<b>'+e(x.value)+'</b><br><span class="muted">'+e(x.source)+' · '+e(x.time)+'</span>')).join('')||empty('No observations yet.');document.getElementById('candidates').innerHTML=c.slice(0,20).map(x=>row(x,'<span class="score">'+Math.round(Number(x.score||0)*100)+'%</span> · <b>'+e(x.fossil_type)+'</b><br>'+e(x.value)+'<br><span class="muted">'+e(x.status)+'</span>')).join('')||empty('No candidates yet.');document.getElementById('lifecycle').innerHTML=l.map(x=>row(x,'<b>'+e(x.state)+'</b><br>'+e(x.value))).join('')||empty('No lifecycle observations yet.');document.querySelectorAll('[data-x]').forEach(n=>{const open=()=>openDrawer(JSON.parse(decodeURIComponent(n.dataset.x)));n.onclick=open;n.onkeydown=ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();open()}}})}function openDrawer(v){document.getElementById('drawerBody').textContent=JSON.stringify(v,null,2);document.getElementById('drawer').classList.add('open')}document.getElementById('closeDrawer').onclick=()=>document.getElementById('drawer').classList.remove('open');function filterRows(){const q=document.getElementById('search').value.toLowerCase().trim();document.querySelectorAll('[data-x]').forEach(n=>n.style.display=!q||n.textContent.toLowerCase().includes(q)?'':'none')}document.getElementById('searchBtn').onclick=filterRows;document.getElementById('search').addEventListener('keydown',e=>{if(e.key==='Enter')filterRows()});const jobStatus=document.getElementById('jobStatus');try{const events=new EventSource('/api/jobs/events');events.addEventListener('job',event=>{try{const j=JSON.parse(event.data);jobStatus.textContent='Job: '+(j.event_type||'event')+' · '+(j.job_id||'')}catch(_){}});events.onerror=()=>{jobStatus.textContent='Jobs: reconnecting'}}catch(_){jobStatus.textContent='Jobs: unavailable'}load().catch(err=>{document.getElementById('timeline').innerHTML=empty('Unable to load dashboard data: '+err.message)})"""


def create_app(workspace: Path) -> FastAPI:
    workspace = Workspace.initialize(workspace).root
    app = FastAPI(
        title="FossilScope Local API",
        version=__version__,
        description=(
            "Evidence-native local API for temporal security archaeology. FossilScope separates "
            "historical observations from current exposure; analysis endpoints do not create "
            "validated findings merely from historical evidence."
        ),
        redoc_url=None,
        openapi_tags=OPENAPI_TAGS,
    )
    engine = FossilEngine(workspace)
    shared_graph = TemporalGraph(workspace)
    shared_jobs = JobEngine(workspace)
    shared_lineage = EvidenceLineage(workspace)
    shared_notebook = ResearchNotebook(workspace)

    @app.middleware("http")
    async def hdr(req: Any, call_next: Any) -> Any:
        response = await call_next(req)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def root() -> str:
        return HTML.replace("__VERSION__", __version__)

    @app.get("/assets/app.js", include_in_schema=False)
    async def js() -> Response:
        return Response(JS, media_type="application/javascript")

    @app.get(
        "/api/timeline",
        tags=["temporal-research"],
        summary="List temporal observations",
        description="Return workspace observations in temporal order with their source and observation time.",
        response_description="Temporal observations recorded in the current FossilScope workspace.",
    )
    async def timeline() -> list[dict[str, Any]]:
        return engine.timeline()

    @app.get(
        "/api/candidates",
        tags=["temporal-research"],
        summary="List fossil candidates",
        description="Return explainable fossil candidates and prioritization scores. Scores are not vulnerability severity.",
        response_description="Ranked fossil candidate records.",
    )
    async def candidates() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in engine.score()]

    @app.get(
        "/api/lifecycle",
        tags=["temporal-research"],
        summary="Show exposure lifecycle",
        description="Return evidence-derived lifecycle states for observed attack-surface artifacts.",
        response_description="Lifecycle observations for the workspace.",
    )
    async def lifecycle() -> list[dict[str, Any]]:
        return engine.lifecycle()

    @app.get(
        "/api/graph",
        tags=["temporal-research"],
        summary="Get the temporal security graph",
        description="Return the product-native temporal graph snapshot used for historical attack-surface analysis.",
    )
    async def graph() -> dict[str, list[dict[str, Any]]]:
        return engine.temporal_graph()

    @app.get(
        "/api/clusters",
        tags=["temporal-research"],
        summary="List correlated historical clusters",
        description="Return evidence-linked historical clusters without asserting current ownership or exposure from similarity alone.",
    )
    async def clusters() -> list[dict[str, Any]]:
        return engine.clusters()

    @app.get(
        "/api/time-travel",
        tags=["intelligence"],
        summary="Reconstruct the graph at an instant",
        description="Reconstruct FossilScope's temporal view at an ISO-8601 timestamp. Historical presence does not prove current exposure.",
    )
    async def time_travel(
        at: str = Query(..., description="ISO-8601 instant, for example 2026-08-10T12:00:00Z."),
    ) -> dict[str, Any]:
        from datetime import datetime

        return FossilIntelligence(engine).time_travel(datetime.fromisoformat(at.replace("Z", "+00:00")))

    @app.get(
        "/api/resurrections",
        tags=["intelligence"],
        summary="Find resurrection candidates",
        description="Identify artifacts that disappear and later reappear after a configurable observation gap. Results remain hypotheses until re-observed.",
    )
    async def resurrections(
        min_gap_days: int = Query(180, ge=1, description="Minimum gap in days between observations."),
    ) -> list[dict[str, Any]]:
        return FossilIntelligence(engine).resurrection_candidates(min_gap_days=min_gap_days)

    @app.get(
        "/api/confidence-v2",
        tags=["intelligence"],
        summary="Explain temporal confidence",
        description="Explain confidence, source evidence and temporal decay for one observed value.",
    )
    async def confidence_v2(
        value: str = Query(..., description="Observed artifact value to explain."),
        stale_after_days: int = Query(365, ge=1, description="Age threshold after which historical evidence is considered stale."),
    ) -> dict[str, Any]:
        return FossilIntelligence(engine).confidence_v2(value, stale_after_days)

    @app.get(
        "/api/search",
        tags=["research-runtime"],
        summary="Search the shared temporal graph",
        description="Search indexed SRIC graph records in the current local workspace.",
    )
    async def search(
        q: str = Query(..., min_length=1, description="Case-insensitive graph search text."),
        limit: int = Query(50, ge=1, le=500, description="Maximum number of matching records."),
    ) -> list[dict[str, Any]]:
        return shared_graph.search(q, limit)

    @app.get(
        "/api/jobs",
        tags=["research-runtime"],
        summary="List research jobs",
        description="Return persisted SRIC jobs for the current workspace, including current status and safe metadata.",
    )
    async def jobs() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in shared_jobs.list()]

    @app.get(
        "/api/jobs/events",
        tags=["research-runtime"],
        summary="Stream research job events",
        description="Server-Sent Events stream for job activity. Use once=true for a bounded single poll.",
        response_description="text/event-stream containing job or heartbeat events.",
    )
    async def job_events(
        cursor: int = Query(0, ge=0, description="Zero-based event cursor."),
        once: bool = Query(False, description="Return currently available events and close the stream."),
    ) -> StreamingResponse:
        async def stream() -> Any:
            current = cursor
            while True:
                events = shared_jobs.all_events(current)
                for event in events:
                    payload = json.dumps(event.model_dump(mode="json"), default=str)
                    yield f"id: {current}\nevent: job\ndata: {payload}\n\n"
                    current += 1
                if once:
                    if not events:
                        yield "event: heartbeat\ndata: {}\n\n"
                    break
                await asyncio.sleep(1.0)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    @app.get(
        "/api/notebook",
        tags=["research-runtime"],
        summary="List research notebook entries",
        description="Return evidence-aware SRIC notebook entries stored in the current workspace.",
    )
    async def notebook() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in shared_notebook.list()]

    @app.get(
        "/api/evidence-lineage/{artifact_id:path}",
        tags=["research-runtime"],
        summary="Explain evidence lineage",
        description="Return provenance and lineage for one artifact identifier. Unknown artifacts are returned explicitly as UNKNOWN rather than fabricated.",
    )
    async def lineage(artifact_id: str) -> dict[str, Any]:
        try:
            return shared_lineage.explain(artifact_id)
        except KeyError:
            return {
                "artifact_id": artifact_id,
                "status": "UNKNOWN",
                "message": "No lineage record found.",
            }

    return app
