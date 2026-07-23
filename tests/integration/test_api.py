from pathlib import Path
from fastapi.testclient import TestClient
from sric.workspace import Workspace
from fossilscope.api import create_app

def test_api(tmp_path:Path)->None:
    ws=Workspace.create(tmp_path,"w");c=TestClient(create_app(ws.root));r=c.get("/");assert r.status_code==200 and "script-src 'self'" in r.headers["content-security-policy"];js=c.get("/assets/app.js");assert js.status_code==200 and "fetch(" in js.text;assert c.get("/api/timeline").json()==[]

def test_v03_api_surfaces(tmp_path:Path)->None:
    ws=Workspace.create(tmp_path,'v03');c=TestClient(create_app(ws.root));assert c.get('/api/resurrections').json()==[];tt=c.get('/api/time-travel',params={'at':'2025-01-01T00:00:00+00:00'});assert tt.status_code==200 and tt.json()['historical_does_not_imply_current_reachability'] is True
