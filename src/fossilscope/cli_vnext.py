from __future__ import annotations
import json,sys
from datetime import datetime
from pathlib import Path
import typer,sric
from sric.plugins import PluginRegistry
from sric.scope import ScopeEngine,ScopePolicy
from sric.workspace import Workspace
from . import cli as base
from .advanced import FossilIntelligence
from .collector_runtime import PassiveHTTPSCollectorRuntime
from .core import FossilEngine
app=base.app;wp=base.wp;root_default=base.root_default
@app.command("doctor")
def doctor_vnext(json_output:bool=typer.Option(False,"--json"),plugin_path:Path=typer.Option(root_default()/"plugins","--plugin-path"))->None:
    plugins=PluginRegistry(plugin_path).list();checks={"python":{"ok":sys.version_info>=(3,11),"version":sys.version.split()[0]},"sric":{"ok":sric.__version__.startswith("0.4."),"version":sric.__version__},"ai":{"ok":True,"mode":"disabled","cloud_uploads":False},"plugins":{"ok":True,"count":len(plugins)},"privacy":{"ok":True,"telemetry":False}};ok=all(bool(v["ok"]) for v in checks.values());typer.echo(json.dumps({"ok":ok,"checks":checks},indent=2) if json_output else "\n".join(f"[{'OK' if v['ok'] else 'FAIL'}] {k}: {v}" for k,v in checks.items()));
    if not ok:raise typer.Exit(1)
@app.command("collect-url")
def collect_url(workspace:str,url:str,adapter:str,allow:list[str]=typer.Option([],"--allow"),ack_terms:bool=typer.Option(False,"--ack-terms"),cache_ttl:int=typer.Option(3600,"--cache-ttl",min=0),root:Path=typer.Option(root_default(),"--root"))->None:
    if not allow:typer.echo("collect-url requires at least one --allow target; no network request was sent",err=True);raise typer.Exit(3)
    workspace_path=wp(workspace,root);Workspace.open(workspace_path);runtime=PassiveHTTPSCollectorRuntime(workspace_path/"fossilscope"/"collector-cache",ScopeEngine(ScopePolicy(allow_targets=allow,allowed_methods={"GET"})),ttl_seconds=cache_ttl)
    try:result=runtime.collect(url,adapter,ack_terms=ack_terms)
    except (PermissionError,ValueError) as exc:typer.echo(str(exc),err=True);raise typer.Exit(3)
    engine=FossilEngine(workspace_path)
    for obs in result.observations:engine.add_observation(obs)
    typer.echo(json.dumps({"mode":"PASSIVE_GET_ONLY","url":result.url,"cache_hit":result.cache_hit,"sha256":result.sha256,"size_bytes":result.size_bytes,"imported":len(result.observations),"provenance":result.provenance},indent=2))
@app.command("time-travel")
def time_travel(workspace:str,at:str=typer.Option(...,"--at"),root:Path=typer.Option(root_default(),"--root"))->None:
    try:when=datetime.fromisoformat(at.replace("Z","+00:00"))
    except ValueError:typer.echo("--at must be ISO-8601",err=True);raise typer.Exit(2)
    typer.echo(json.dumps(FossilIntelligence(FossilEngine(wp(workspace,root))).time_travel(when),indent=2,default=str))
@app.command("resurrections")
def resurrections(workspace:str,min_gap_days:int=typer.Option(180,"--min-gap-days",min=1),root:Path=typer.Option(root_default(),"--root"))->None:typer.echo(json.dumps(FossilIntelligence(FossilEngine(wp(workspace,root))).resurrection_candidates(min_gap_days=min_gap_days),indent=2,default=str))
@app.command("confidence-v2")
def confidence_v2(workspace:str,value:str,stale_after_days:int=typer.Option(365,"--stale-after-days",min=1),root:Path=typer.Option(root_default(),"--root"))->None:
    try:payload=FossilIntelligence(FossilEngine(wp(workspace,root))).confidence_v2(value,stale_after_days)
    except KeyError:typer.echo("Observation value not found",err=True);raise typer.Exit(2)
    typer.echo(json.dumps(payload,indent=2,default=str))
@app.command("mobile-archaeology")
def mobile_archaeology(workspace:str,old_artifact:Path,new_artifact:Path,root:Path=typer.Option(root_default(),"--root"))->None:
    if not old_artifact.is_file() or not new_artifact.is_file():typer.echo("Both artifacts must be regular files",err=True);raise typer.Exit(2)
    typer.echo(json.dumps(FossilIntelligence(FossilEngine(wp(workspace,root))).mobile_api_archaeology(old_artifact,new_artifact),indent=2,default=str))
def run()->None:base.run()
