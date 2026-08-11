from __future__ import annotations

import hashlib
import json
import socket
import ssl
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from sric.rate_limit import RateLimiter,RateLimitPolicy
from sric.scope import ScopeEngine
from .collectors import collect_passive
from .models import Observation

@dataclass(frozen=True)
class CollectorFetchResult:
    url:str;cache_hit:bool;sha256:str;size_bytes:int;observations:list[Observation];provenance:dict[str,object]

class PassiveHTTPSCollectorRuntime:
    """Bounded HTTPS-only opt-in passive collector with scope, DNS pinning, no redirects and cache."""
    def __init__(self,cache_dir:Path,scope:ScopeEngine,*,max_bytes:int=10*1024*1024,ttl_seconds:int=3600,rate_limiter:RateLimiter|None=None)->None:
        self.cache_dir=cache_dir;self.cache_dir.mkdir(parents=True,exist_ok=True);self.scope=scope;self.max_bytes=max_bytes;self.ttl_seconds=ttl_seconds;self.rate=rate_limiter or RateLimiter(RateLimitPolicy(global_rps=2,per_host_rps=1))
    def _fetch(self,url:str)->bytes:
        parsed=urlsplit(url)
        if parsed.scheme!="https" or not parsed.hostname:raise ValueError("collector network sources require HTTPS")
        if parsed.username or parsed.password:raise ValueError("credentials in collector URLs are forbidden")
        pre=self.scope.evaluate(url,"GET")
        if not pre.allowed:raise PermissionError(f"scope denied collector source: {pre.reason}")
        infos=socket.getaddrinfo(parsed.hostname,parsed.port or 443,type=socket.SOCK_STREAM);ips=sorted({str(x[4][0]) for x in infos});resolved=self.scope.evaluate(url,"GET",resolved_ips=ips)
        if not resolved.allowed:raise PermissionError(f"resolved collector source denied: {resolved.reason}")
        self.rate.acquire(parsed.hostname);sock=socket.create_connection((ips[0],parsed.port or 443),timeout=15);tls=ssl.create_default_context().wrap_socket(sock,server_hostname=parsed.hostname)
        try:
            path=parsed.path or "/";path+=f"?{parsed.query}" if parsed.query else "";tls.sendall((f"GET {path} HTTP/1.1\r\nHost: {parsed.hostname}\r\nUser-Agent: FossilScope/0.3 passive-collector\r\nAccept: application/json,text/plain,*/*\r\nConnection: close\r\n\r\n").encode());f=tls.makefile("rb");status=f.readline().decode("iso-8859-1").strip();parts=status.split()
            if len(parts)<2 or not parts[1].isdigit():raise ValueError("invalid collector HTTP response")
            code=int(parts[1]);headers={}
            while True:
                line=f.readline()
                if line in {b"\r\n",b"\n",b""}:break
                name,_,value=line.decode("iso-8859-1").partition(":");headers[name.strip().lower()]=value.strip()
            if 300<=code<400:raise PermissionError("collector redirects are disabled; validate final source explicitly")
            if code<200 or code>=300:raise ValueError(f"collector source returned HTTP {code}")
            if headers.get("transfer-encoding","").lower()=="chunked":raise ValueError("chunked collector responses unsupported by pinned minimal fetcher")
            declared=headers.get("content-length")
            if declared and declared.isdigit() and int(declared)>self.max_bytes:raise ValueError("collector response exceeds size limit")
            data=f.read(self.max_bytes+1)
            if len(data)>self.max_bytes:raise ValueError("collector response exceeds size limit")
            return data
        finally:tls.close()
    def collect(self,url:str,adapter:str,*,ack_terms:bool=False)->CollectorFetchResult:
        if not ack_terms:raise PermissionError("network collector requires explicit terms/source acknowledgement")
        key=hashlib.sha256(url.encode()).hexdigest();blob=self.cache_dir/f"{key}.bin";meta=self.cache_dir/f"{key}.json";cache_hit=False
        if blob.is_file() and meta.is_file() and time.time()-float(json.loads(meta.read_text()).get("fetched_epoch",0))<=self.ttl_seconds:data=blob.read_bytes();cache_hit=True
        else:data=self._fetch(url)
        digest=hashlib.sha256(data).hexdigest()
        if not cache_hit:
            blob.write_bytes(data);meta.write_text(json.dumps({"url":url,"sha256":digest,"fetched_epoch":time.time(),"fetched_at":datetime.now(timezone.utc).isoformat()},indent=2),encoding="utf-8")
        with tempfile.NamedTemporaryFile(delete=False,suffix=".json") as fh:tmp=Path(fh.name);fh.write(data)
        try:observations=collect_passive(tmp,adapter)
        finally:tmp.unlink(missing_ok=True)
        provenance={"source_url":url,"sha256":digest,"cache_hit":cache_hit,"adapter":adapter,"terms_acknowledged":True,"network_mode":"PASSIVE_GET_ONLY"}
        for obs in observations:obs.metadata={**obs.metadata,"collector_provenance":provenance}
        return CollectorFetchResult(url,cache_hit,digest,len(data),observations,provenance)
