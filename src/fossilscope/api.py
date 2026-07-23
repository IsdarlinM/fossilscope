from __future__ import annotations

import asyncio,json
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse,HTMLResponse,Response
from . import __version__
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import ResearchNotebook
from .core import FossilEngine
from .advanced import FossilIntelligence

HTML="""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FossilScope</title><style>body{font-family:system-ui;margin:0;background:#10120f;color:#edf0e8}header{padding:18px 24px;border-bottom:1px solid #384033;display:flex;justify-content:space-between}main{padding:24px;display:grid;gap:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{background:#181d16;border:1px solid #384033;border-radius:12px;padding:18px}.muted{color:#aeb9a6}.row{padding:10px 0;border-bottom:1px solid #323a2f}.score{font-variant-numeric:tabular-nums;font-weight:700}input,button{background:#11170f;color:#edf0e8;border:1px solid #384033;border-radius:8px;padding:8px}.drawer{position:fixed;right:0;top:0;height:100%;width:min(480px,90vw);background:#151a13;border-left:1px solid #384033;padding:20px;display:none;overflow:auto}.drawer.open{display:block}</style></head><body><header><b>FossilScope</b><span>imr :: v__VERSION__ · PASSIVE</span><span id='jobStatus' class='muted'>Jobs: idle</span></header><main><div><input id='search' placeholder='Search timeline/candidates'><button id='searchBtn'>Search</button></div><div class='grid'><div class='card'><h3>Temporal Security Graph</h3><p class='muted'>Historical evidence remains separate from current reachability.</p><div id='timeline'></div></div><div class='card'><h3>Fossil Candidates</h3><p class='muted'>Explainable score components; never vulnerability severity.</p><div id='candidates'></div></div><div class='card'><h3>Lifecycle</h3><div id='lifecycle'></div></div></div></main><aside id='drawer' class='drawer'><button id='closeDrawer'>Close</button><h3>Evidence / Explainability</h3><pre id='drawerBody'></pre></aside><script src='/assets/app.js'></script></body></html>"""
JS="""function e(v){return String(v).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}function row(v,html){return '<div class=row data-x=\''+encodeURIComponent(JSON.stringify(v))+'\'>'+html+'</div>'}async function load(){const t=await fetch('/api/timeline').then(r=>r.json());document.getElementById('timeline').innerHTML=t.slice(-20).reverse().map(x=>row(x,'<b>'+e(x.value)+'</b><br><span class=muted>'+e(x.source)+' · '+e(x.time)+'</span>')).join('')||'<p class=muted>No observations yet.</p>';const c=await fetch('/api/candidates').then(r=>r.json());document.getElementById('candidates').innerHTML=c.slice(0,20).map(x=>row(x,'<span class=score>'+Math.round(x.score*100)+'%</span> · <b>'+e(x.fossil_type)+'</b><br>'+e(x.value)+'<br><span class=muted>'+e(x.status)+'</span>')).join('')||'<p class=muted>No candidates yet.</p>';const l=await fetch('/api/lifecycle').then(r=>r.json());document.getElementById('lifecycle').innerHTML=l.map(x=>row(x,'<b>'+e(x.state)+'</b><br>'+e(x.value))).join('');document.querySelectorAll('[data-x]').forEach(n=>n.onclick=()=>openDrawer(JSON.parse(decodeURIComponent(n.dataset.x))))}function openDrawer(v){document.getElementById('drawerBody').textContent=JSON.stringify(v,null,2);document.getElementById('drawer').classList.add('open')}document.getElementById('closeDrawer').onclick=()=>document.getElementById('drawer').classList.remove('open');document.getElementById('searchBtn').onclick=()=>{const q=document.getElementById('search').value.toLowerCase();document.querySelectorAll('[data-x]').forEach(n=>n.style.display=n.textContent.toLowerCase().includes(q)?'':'none')};const jobStatus=document.getElementById('jobStatus');try{const events=new EventSource('/api/jobs/events');events.addEventListener('job',e=>{try{const j=JSON.parse(e.data);jobStatus.textContent='Job: '+(j.event_type||'event')+' · '+(j.job_id||'');}catch(_){}})}catch(_){}load().catch(()=>{});"""

def create_app(workspace:Path)->FastAPI:
    app=FastAPI(title="FossilScope Local API",version=__version__,redoc_url=None);engine=FossilEngine(workspace);shared_graph=TemporalGraph(workspace);shared_jobs=JobEngine(workspace);shared_lineage=EvidenceLineage(workspace);shared_notebook=ResearchNotebook(workspace)
    @app.middleware("http")
    async def hdr(req:Any,call_next:Any)->Any:
        response=await call_next(req);response.headers["Content-Security-Policy"]="default-src 'self'; script-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'";response.headers["X-Content-Type-Options"]="nosniff";response.headers["Referrer-Policy"]="no-referrer";return response
    @app.get("/",response_class=HTMLResponse)
    async def root()->str:return HTML.replace("__VERSION__",__version__)
    @app.get("/assets/app.js")
    async def js()->Response:return Response(JS,media_type="application/javascript")
    @app.get("/api/timeline")
    async def timeline()->list[dict[str,Any]]:return engine.timeline()
    @app.get("/api/candidates")
    async def candidates()->list[dict[str,Any]]:return [x.model_dump(mode="json") for x in engine.score()]
    @app.get("/api/lifecycle")
    async def lifecycle()->list[dict[str,Any]]:return engine.lifecycle()
    @app.get("/api/graph")
    async def graph()->dict[str,list[dict[str,Any]]]:return engine.temporal_graph()
    @app.get("/api/clusters")
    async def clusters()->list[dict[str,Any]]:return engine.clusters()
    @app.get("/api/time-travel")
    async def time_travel(at:str)->dict[str,Any]:
        from datetime import datetime
        return FossilIntelligence(engine).time_travel(datetime.fromisoformat(at.replace("Z","+00:00")))
    @app.get("/api/resurrections")
    async def resurrections(min_gap_days:int=180)->list[dict[str,Any]]:return FossilIntelligence(engine).resurrection_candidates(min_gap_days=max(1,min_gap_days))
    @app.get("/api/confidence-v2")
    async def confidence_v2(value:str,stale_after_days:int=365)->dict[str,Any]:return FossilIntelligence(engine).confidence_v2(value,max(1,stale_after_days))
    @app.get("/api/search")
    async def search(q:str,limit:int=50)->list[dict[str,Any]]:return shared_graph.search(q,max(1,min(limit,500)))
    @app.get("/api/jobs")
    async def jobs()->list[dict[str,Any]]:return [x.model_dump(mode="json") for x in shared_jobs.list()]
    @app.get("/api/jobs/events")
    async def job_events(cursor:int=0,once:bool=False)->StreamingResponse:
        async def stream()->Any:
            current=max(0,cursor)
            while True:
                events=shared_jobs.all_events(current)
                for event in events:
                    payload=json.dumps(event.model_dump(mode="json"),default=str);yield f"id: {current}\nevent: job\ndata: {payload}\n\n";current+=1
                if once:
                    if not events:yield "event: heartbeat\ndata: {}\n\n"
                    break
                await asyncio.sleep(1.0)
        return StreamingResponse(stream(),media_type="text/event-stream",headers={"Cache-Control":"no-store","X-Accel-Buffering":"no"})
    @app.get("/api/notebook")
    async def notebook()->list[dict[str,Any]]:return [x.model_dump(mode="json") for x in shared_notebook.list()]
    @app.get("/api/evidence-lineage/{artifact_id:path}")
    async def lineage(artifact_id:str)->dict[str,Any]:
        try:return shared_lineage.explain(artifact_id)
        except KeyError:return {"artifact_id":artifact_id,"status":"UNKNOWN","message":"No lineage record found."}
    return app
