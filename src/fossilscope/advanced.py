from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .collectors import collect_passive
from .models import Observation


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


class FossilIntelligence:
    def __init__(self, engine: Any) -> None:
        self.engine=engine

    def time_travel(self, at: datetime) -> dict[str, Any]:
        snapshot=self.engine.temporal_graph(at);lifecycle=self.engine.lifecycle();states={x['value']:x['state'] for x in lifecycle}
        for node in snapshot['nodes']:
            node['lifecycle_state']=states.get(node.get('label'),'DISCOVERED')
        return {"at":_aware(at).isoformat(),"graph":snapshot,"legend":["APPEARED","DISAPPEARED","CHANGED","REAPPEARED","HISTORICAL_ONLY","CURRENTLY_REFERENCED","REACHABILITY_UNKNOWN","CURRENTLY_REACHABLE"],"historical_does_not_imply_current_reachability":True}

    def resurrection_candidates(self, *, min_gap_days: int = 180) -> list[dict[str, Any]]:
        data=self.engine.store.load();by=defaultdict(list)
        for raw in data['observations']:
            o=Observation.model_validate(raw);by[o.value].append(o)
        out=[]
        for value,items in sorted(by.items()):
            moments=[]
            for o in items:moments.extend([x for x in (o.first_seen,o.last_seen,o.observed_at) if x is not None])
            moments=sorted({_aware(x) for x in moments});gaps=[(moments[i]-moments[i-1]).days for i in range(1,len(moments))]
            has_old=any(o.last_seen is not None for o in items);has_new=any(o.current_reference or o.current_reachable is True for o in items)
            if has_old and has_new and gaps and max(gaps)>=min_gap_days:
                out.append({"value":value,"state":"RESURRECTED","max_gap_days":max(gaps),"status":"HYPOTHESIS","evidence_ids":sorted({e for o in items for e in o.evidence_ids}),"explanation":["Historical presence and a later current reference/reachability observation are separated by a substantial gap.","Resurrection is a temporal signal, not a vulnerability finding."]})
        return out

    def confidence_v2(self, value: str, stale_after_days: int=365) -> dict[str, Any]:
        observations=[Observation.model_validate(x) for x in self.engine.store.load()['observations'] if x['value']==value]
        if not observations:raise KeyError(value)
        sources={o.source for o in observations};historical_times=[_aware(o.first_seen or o.observed_at) for o in observations];current_times=[_aware(o.observed_at) for o in observations if o.current_reference or o.current_reachable is not None]
        historical=min(1.0,.45+.12*len(sources)+(.1 if len(historical_times)>1 else 0));latest=max(current_times or historical_times);age=max(0,(datetime.now(timezone.utc)-latest).days);current=max(.05,historical-min(.85,age/max(1,stale_after_days)*.25))
        if any(o.current_reachable is True for o in observations):current=min(1.0,current+.2)
        elif any(o.current_reachable is False for o in observations):current=max(.05,current-.2)
        return {"value":value,"historical_confidence":round(historical,4),"current_confidence":round(current,4),"age_days":age,"source_count":len(sources),"current_reachability":True if any(o.current_reachable is True for o in observations) else (False if any(o.current_reachable is False for o in observations) else None),"principle":"Historical confidence and current exposure confidence are separate."}

    def mobile_api_archaeology(self, old_artifact: Path, new_artifact: Path) -> dict[str, Any]:
        old=collect_passive(old_artifact,'archive');new=collect_passive(new_artifact,'archive');old_values={x.value for x in old};new_values={x.value for x in new}
        legacy=sorted(old_values-new_values);persisting=sorted(old_values&new_values);introduced=sorted(new_values-old_values)
        return {"legacy_only":legacy,"persisting":persisting,"introduced":introduced,"legacy_identity_auth_candidates":[x for x in legacy if any(k in x.casefold() for k in ('auth','oauth','login','token','identity'))],"status":"HYPOTHESIS","network_requests_performed":False}
