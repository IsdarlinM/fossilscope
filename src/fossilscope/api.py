from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import ResearchNotebook

from . import __version__
from .advanced import FossilIntelligence
from .core import FossilEngine

HTML = """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FossilScope</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{font-family:system-ui,-apple-system,sans-serif;margin:0;background:#0d110e;color:#edf0e8}header{padding:14px 18px;border-bottom:1px solid #384033;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;background:#101510}.brand{display:flex;align-items:center;gap:12px}.brand small{color:#98aa98}.nav{display:flex;gap:7px;align-items:center;overflow:auto}.nav a{white-space:nowrap;text-decoration:none;color:#d9e5d7;border:1px solid #3a4938;border-radius:999px;padding:7px 10px;font-size:12px}.nav a.primary{background:#18321f;border-color:#4d7957;color:#dff4e3}.status{color:#9aac9a;font-size:12px}main{padding:20px;display:grid;gap:14px;max-width:1500px;margin:auto}.hero{display:flex;align-items:center;justify-content:space-between;gap:12px}.search{display:flex;gap:7px;min-width:min(100%,420px)}.search input{flex:1}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{background:#151b15;border:1px solid #354035;border-radius:12px;padding:17px;min-width:0}.card h3{margin-top:0}.muted{color:#9fac9e}.row{padding:10px 0;border-bottom:1px solid #2d372d;cursor:pointer}.row:hover{background:#121712}.score{font-variant-numeric:tabular-nums;font-weight:700}input,button{background:#101610;color:#edf0e8;border:1px solid #384b39;border-radius:8px;padding:9px}button{cursor:pointer}.drawer{position:fixed;right:0;top:0;height:100%;width:min(480px,92vw);background:#131913;border-left:1px solid #384033;padding:20px;display:none;overflow:auto;z-index:40}.drawer.open{display:block}pre{white-space:pre-wrap;word-break:break-word}.feature-callout{border:1px solid #3f6649;background:#111d14;border-radius:12px;padding:14px}.feature-callout a{color:#b8e8c2;font-weight:700}@media(max-width:650px){header{align-items:flex-start}.brand{width:100%;justify-content:space-between}.nav{width:100%;padding-bottom:2px}.hero{align-items:stretch;flex-direction:column}.search{min-width:0;width:100%}main{padding:12px}.grid{grid-template-columns:1fr}.card{padding:14px}}</style></head><body><header><div class='brand'><b>FossilScope</b><small>imr :: v__VERSION__ · PASSIVE</small></div><nav class='nav' aria-label='FossilScope Web navigation'><a href='/' aria-current='page'>Dashboard</a><a class='primary' href='/workbench'>Security Console</a><a href='/docs'>API</a></nav><span id='jobStatus' class='status'>Jobs: idle</span></header><main><section class='feature-callout'><strong>Guided operations:</strong> this dashboard remains the quick temporal view. <a href='/workbench'>Open Security Console</a> to configure FossilScope capabilities with typed controls instead of command syntax.</section><div class='hero'><div><h2>Temporal research workspace</h2><div class='muted'>Historical evidence remains separate from current exposure.</div></div><div class='search'><input id='search' placeholder='Search timeline/candidates' aria-label='Search timeline and candidates'><button id='searchBtn'>Search</button></div></div><div class='grid'><div class='card'><h3>Temporal Security Graph</h3><p class='muted'>Historical evidence remains separate from current reachability.</p><div id='timeline'></div></div><div class='card'><h3>Fossil Candidates</h3><p class='muted'>Explainable score components; never vulnerability severity.</p><div id='candidates'></div></div><div class='card'><h3>Lifecycle</h3><div id='lifecycle'></div></div></div></main><aside id='drawer' class='drawer'><button id='closeDrawer'>Close</button><h3>Evidence / Explainability</h3><pre id='drawerBody'></pre></aside><script src='/assets/app.js'></script></body></html>"""

JS = """function e(v){return String(v).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}function row(v,html){return '<div class=row data-x=\''+encodeURIComponent(JSON.stringify(v))+'\'>'+html+'</div>'}async function load(){const t=await fetch('/api/timeline').then(r=>r.json());document.getElementById('timeline').innerHTML=t.slice(-20).reverse().map(x=>row(x,'<b>'+e(x.value)+'</b><br><span class=muted>'+e(x.source)+' · '+e(x.time)+'</span>')).join('')||'<p class=muted>No observations yet.</p>';const c=await fetch('/api/candidates').then(r=>r.json());document.getElementById('candidates').innerHTML=c.slice(0,20).map(x=>row(x,'<span class=score>'+Math.round(x.score*100)+'%</span> · <b>'+e(x.fossil_type)+'</b><br>'+e(x.value)+'<br><span class=muted>'+e(x.status)+'</span>')).join('')||'<p class=muted>No candidates yet.</p>';const l=await fetch('/api/lifecycle').then(r=>r.json());document.getElementById('lifecycle').innerHTML=l.map(x=>row(x,'<b>'+e(x.state)+'</b><br>'+e(x.value))).join('')||'<p class=muted>No lifecycle observations yet.</p>';document.querySelectorAll('[data-x]').forEach(n=>n.onclick=()=>openDrawer(JSON.parse(decodeURIComponent(n.dataset.x))))}function openDrawer(v){document.getElementById('drawerBody').textContent=JSON.stringify(v,null,2);document.getElementById('drawer').classList.add('open')}document.getElementById('closeDrawer').onclick=()=>document.getElementById('drawer').classList.remove('open');document.getElementById('searchBtn').onclick=()=>{const q=document.getElementById('search').value.toLowerCase();document.querySelectorAll('[data-x]').forEach(n=>n.style.display=n.textContent.toLowerCase().includes(q)?'':'none')};const jobStatus=document.getElementById('jobStatus');try{const events=new EventSource('/api/jobs/events');events.addEventListener('job',event=>{try{const j=JSON.parse(event.data);jobStatus.textContent='Job: '+(j.event_type||'event')+' · '+(j.job_id||'')}catch(_){}});events.onerror=()=>{jobStatus.textContent='Jobs: reconnecting'}}catch(_){jobStatus.textContent='Jobs: unavailable'}load().catch(()=>{})"""


def create_app(workspace: Path) -> FastAPI:
    app = FastAPI(title="FossilScope Local API", version=__version__, redoc_url=None)
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

    @app.get("/", response_class=HTMLResponse)
    async def root() -> str:
        return HTML.replace("__VERSION__", __version__)

    @app.get("/assets/app.js")
    async def js() -> Response:
        return Response(JS, media_type="application/javascript")

    @app.get("/api/timeline")
    async def timeline() -> list[dict[str, Any]]:
        return engine.timeline()

    @app.get("/api/candidates")
    async def candidates() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in engine.score()]

    @app.get("/api/lifecycle")
    async def lifecycle() -> list[dict[str, Any]]:
        return engine.lifecycle()

    @app.get("/api/graph")
    async def graph() -> dict[str, list[dict[str, Any]]]:
        return engine.temporal_graph()

    @app.get("/api/clusters")
    async def clusters() -> list[dict[str, Any]]:
        return engine.clusters()

    @app.get("/api/time-travel")
    async def time_travel(at: str) -> dict[str, Any]:
        from datetime import datetime

        return FossilIntelligence(engine).time_travel(datetime.fromisoformat(at.replace("Z", "+00:00")))

    @app.get("/api/resurrections")
    async def resurrections(min_gap_days: int = 180) -> list[dict[str, Any]]:
        return FossilIntelligence(engine).resurrection_candidates(min_gap_days=max(1, min_gap_days))

    @app.get("/api/confidence-v2")
    async def confidence_v2(value: str, stale_after_days: int = 365) -> dict[str, Any]:
        return FossilIntelligence(engine).confidence_v2(value, max(1, stale_after_days))

    @app.get("/api/search")
    async def search(q: str, limit: int = 50) -> list[dict[str, Any]]:
        return shared_graph.search(q, max(1, min(limit, 500)))

    @app.get("/api/jobs")
    async def jobs() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in shared_jobs.list()]

    @app.get("/api/jobs/events")
    async def job_events(cursor: int = 0, once: bool = False) -> StreamingResponse:
        async def stream() -> Any:
            current = max(0, cursor)
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

    @app.get("/api/notebook")
    async def notebook() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in shared_notebook.list()]

    @app.get("/api/evidence-lineage/{artifact_id:path}")
    async def lineage(artifact_id: str) -> dict[str, Any]:
        try:
            return shared_lineage.explain(artifact_id)
        except KeyError:
            return {"artifact_id": artifact_id, "status": "UNKNOWN", "message": "No lineage record found."}

    return app
