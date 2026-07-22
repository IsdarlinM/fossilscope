from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .models import FossilCandidate, FossilType, Observation, Relationship
from .store import JsonStore
from sric.graph import GraphEdge, GraphNode, TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage, LineageRecord


MAX_IMPORT_BYTES = 10 * 1024 * 1024


def _load_json_file(path: Path) -> Any:
    if not path.is_file() or path.is_symlink():
        raise ValueError("import path must be a regular non-symlink file")
    size = path.stat().st_size
    if size > MAX_IMPORT_BYTES:
        raise ValueError(f"import exceeds {MAX_IMPORT_BYTES} byte limit")
    return __import__("json").loads(path.read_text(encoding="utf-8"))


def _upsert(items: list[dict[str, Any]], key: str, value: dict[str, Any]) -> None:
    for i, x in enumerate(items):
        if x.get(key) == value.get(key):
            items[i] = value
            return
    items.append(value)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def _age_score(last_seen: datetime | None) -> float:
    if last_seen is None:
        return 0.45
    last_seen = _aware(last_seen)
    days = max(0, (datetime.now(timezone.utc) - last_seen).days)
    return min(1.0, days / 1460)


def infer_type(obs: Observation) -> FossilType:
    t = obs.entity_type.lower()
    v = obs.value.lower()
    if "oauth" in t or "client" in t:
        return FossilType.ORPHANED_CLIENT
    if "sdk" in t or "package" in t:
        return FossilType.OLD_SDK_REFERENCE
    if "doc" in t:
        return FossilType.STALE_DOCUMENTATION
    if "storage" in t or "bucket" in t:
        return FossilType.OLD_STORAGE_REFERENCE
    if "auth" in v:
        return FossilType.LEGACY_AUTH_PATH
    if "endpoint" in t or "api" in t:
        return FossilType.DEPRECATED_API
    return FossilType.GHOST_DOMAIN


class FossilEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.store = JsonStore(workspace)
        self.graph_store = TemporalGraph(workspace)
        self.jobs = JobEngine(workspace)
        self.lineage = EvidenceLineage(workspace)

    def add_observation(self, obs: Observation) -> None:
        data = self.store.load()
        _upsert(data["observations"], "observation_id", obs.model_dump(mode="json"))
        self.store.save(data)
        node = GraphNode(node_id=f"fossil:{obs.value}", node_type=obs.entity_type, label=obs.value, source=obs.source, first_seen=obs.first_seen, last_seen=obs.last_seen, observed_at=obs.observed_at, evidence_ids=obs.evidence_ids, metadata={"current_reachable": obs.current_reachable, "auth_relevance": obs.auth_relevance, "current_reference": obs.current_reference})
        self.graph_store.upsert_node(node)
        self._lineage_once(LineageRecord(artifact_id=f"observation:{obs.observation_id}", artifact_type="temporal_observation", status="OBSERVED", source=obs.source, method="ingest", evidence_ids=obs.evidence_ids))

    def add_relationship(self, rel: Relationship) -> None:
        data = self.store.load()
        _upsert(data["relationships"], "relationship_id", rel.model_dump(mode="json"))
        self.store.save(data)
        for value in (rel.source_value, rel.target_value):
            try:
                self.graph_store.upsert_node(GraphNode(node_id=f"fossil:{value}", node_type="unknown", label=value, source="relationship_import"))
            except Exception:
                pass
        self.graph_store.upsert_edge(GraphEdge(edge_id=f"fossil-rel:{rel.relationship_id}", source_node_id=f"fossil:{rel.source_value}", target_node_id=f"fossil:{rel.target_value}", edge_type=rel.relationship_type, valid_from=rel.valid_from, valid_to=rel.valid_to, observed_at=rel.observed_at, confidence=rel.confidence, evidence_ids=rel.evidence_ids, discovery_method="fossilscope_relationship"))

    def import_json(self, path: Path) -> int:
        raw = path.read_text(encoding="utf-8")
        payload = __import__("json").loads(raw)
        items = payload if isinstance(payload, list) else payload.get("observations", [])
        count = 0
        for x in items:
            self.add_observation(Observation.model_validate(x))
            count += 1
        return count

    def collect_adapter(self, path: Path, adapter: str) -> int:
        """Ingest an explicit local export through a passive source adapter.

        Adapters normalize user-supplied data only; they never crawl or probe targets.
        """
        from .collectors import collect_passive

        observations = collect_passive(path, adapter)
        for observation in observations:
            self.add_observation(observation)
        return len(observations)

    def extract_artifact(self, path: Path, source: str) -> int:
        """Passively extract URL/domain references from a local text artifact."""
        import re
        import hashlib

        if not path.is_file() or path.is_symlink():
            raise ValueError("artifact must be a regular non-symlink file")
        if path.stat().st_size > MAX_IMPORT_BYTES:
            raise ValueError(f"artifact exceeds {MAX_IMPORT_BYTES} byte limit")
        text = path.read_text(encoding="utf-8", errors="replace")
        urls = set(re.findall(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+", text))
        domains = set(re.findall(r"(?<![@\w.-])(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,63}(?![\w.-])", text))
        values = [("endpoint", u.rstrip(".,;)'\"")) for u in urls]
        values += [("domain", d.lower()) for d in domains if not any(d in u for u in urls)]
        for entity_type, value in sorted(set(values)):
            oid = "EXT-" + hashlib.sha256(f"{source}:{value}".encode()).hexdigest()[:12]
            self.add_observation(
                Observation(
                    observation_id=oid,
                    entity_type=entity_type,
                    value=value,
                    source=source,
                    current_reference=True,
                    metadata={"artifact": path.name, "extraction": "deterministic_regex"},
                )
            )
        return len(set(values))

    def timeline(self) -> list[dict[str, Any]]:
        data = self.store.load()
        out = []
        for x in data["observations"]:
            o = Observation.model_validate(x)
            out.append(
                {
                    "time": o.observed_at.isoformat(),
                    "first_seen": o.first_seen.isoformat() if o.first_seen else None,
                    "last_seen": o.last_seen.isoformat() if o.last_seen else None,
                    "value": o.value,
                    "entity_type": o.entity_type,
                    "source": o.source,
                }
            )
        return sorted(out, key=lambda x: x["time"])

    def diff(self, before: datetime, after: datetime) -> dict[str, list[str]]:
        data = self.store.load()
        old = set()
        new = set()
        for x in data["observations"]:
            o = Observation.model_validate(x)
            seen = _aware(o.observed_at)
            before_aware = _aware(before)
            after_aware = _aware(after)
            if seen <= before_aware:
                old.add(o.value)
            if seen <= after_aware:
                new.add(o.value)
        return {
            "added": sorted(new - old),
            "removed": sorted(old - new),
            "present_before": sorted(old),
            "present_after": sorted(new),
        }

    def score(self) -> list[FossilCandidate]:
        data = self.store.load()
        by_value: dict[str, list[Observation]] = defaultdict(list)
        for x in data["observations"]:
            by_value[x["value"]].append(Observation.model_validate(x))
        out: list[FossilCandidate] = []
        for value, obses in sorted(by_value.items()):
            sources = {o.source for o in obses}
            historical_last_seen = [
                _aware(o.last_seen)
                for o in obses
                if o.last_seen is not None and not o.current_reference
            ]
            staleness_anchor = (
                max(historical_last_seen)
                if historical_last_seen
                else max(_aware(o.last_seen or o.observed_at) for o in obses)
            )
            reach = [o.current_reachable for o in obses if o.current_reachable is not None]
            recency = _age_score(staleness_anchor)
            diversity = min(1.0, len(sources) / 3)
            reachability = 1.0 if any(reach) else (0.0 if reach and not any(reach) else 0.35)
            auth = 1.0 if any(o.auth_relevance for o in obses) else 0.0
            sensitive = 1.0 if any(o.sensitivity_hint for o in obses) else 0.0
            refs = 1.0 if any(o.current_reference for o in obses) else 0.0
            # Historical staleness + current reachability/reference make an explainable candidate; stale-only evidence is not enough.
            score = min(
                1.0,
                0.24 * recency
                + 0.18 * diversity
                + 0.22 * reachability
                + 0.14 * auth
                + 0.10 * sensitive
                + 0.12 * refs,
            )
            ev = sorted({e for o in obses for e in o.evidence_ids})
            counter = []
            if reach and not any(reach):
                counter.append("Observed evidence explicitly indicates current_unreachable.")
            if not refs:
                counter.append("No current reference has been observed.")
            out.append(
                FossilCandidate(
                    candidate_id=f"FSL-{len(out) + 1:04d}",
                    value=value,
                    fossil_type=infer_type(obses[-1]),
                    score=round(score, 4),
                    components={
                        "staleness": round(recency, 4),
                        "source_diversity": round(diversity, 4),
                        "current_reachability": reachability,
                        "auth_relevance": auth,
                        "sensitivity_hint": sensitive,
                        "current_reference": refs,
                    },
                    evidence_ids=ev,
                    counter_evidence=counter,
                    explanation=[
                        "Score is a transparent weighted composition, not a vulnerability severity.",
                        "Historical evidence is not treated as proof of current exposure.",
                    ],
                )
            )
        data["candidates"] = [x.model_dump(mode="json") for x in out]
        self.store.save(data)
        return out

    def _lineage_once(self, record: LineageRecord) -> None:
        try:
            self.lineage.explain(record.artifact_id)
        except KeyError:
            self.lineage.append(record)

    def temporal_graph(self, at: datetime | None = None) -> dict[str, list[dict[str, Any]]]:
        return self.graph_store.snapshot(at)

    def lifecycle(self) -> list[dict[str, Any]]:
        """Classify fossil evidence state without conflating historical evidence with exposure."""
        data = self.store.load()
        by_value: dict[str, list[Observation]] = defaultdict(list)
        for raw in data["observations"]:
            by_value[str(raw["value"])].append(Observation.model_validate(raw))
        out: list[dict[str, Any]] = []
        for value, observations in sorted(by_value.items()):
            has_historical = any(o.first_seen or o.last_seen for o in observations)
            current_ref = any(o.current_reference for o in observations)
            reach = [o.current_reachable for o in observations if o.current_reachable is not None]
            if reach and any(reach):
                state = "CURRENTLY_REACHABLE"
            elif current_ref:
                state = "REACHABILITY_UNKNOWN"
            elif has_historical:
                state = "HISTORICAL_ONLY"
            else:
                state = "DISCOVERED"
            out.append({"value": value, "state": state, "historical_evidence": has_historical, "current_reference": current_ref, "current_reachability": True if any(reach) else (False if reach else None), "evidence_ids": sorted({e for o in observations for e in o.evidence_ids})})
        return out

    def historical_api_diff(self, before: Path, after: Path) -> dict[str, list[str]]:
        """Compare supplied OpenAPI-like documents by paths; no network requests are made."""
        old = _load_json_file(before)
        new = _load_json_file(after)
        if not isinstance(old, dict) or not isinstance(new, dict):
            raise ValueError("API diff inputs must be JSON objects")
        old_paths = set(str(x) for x in (old.get("paths") or {}).keys()) if isinstance(old.get("paths"), dict) else set()
        new_paths = set(str(x) for x in (new.get("paths") or {}).keys()) if isinstance(new.get("paths"), dict) else set()
        current_refs = {Observation.model_validate(x).value for x in self.store.load()["observations"] if x.get("current_reference")}
        removed = sorted(old_paths - new_paths)
        still_referenced = sorted(p for p in removed if any(p in ref for ref in current_refs))
        return {"added": sorted(new_paths-old_paths), "removed_from_documentation": removed, "still_referenced": still_referenced}

    def confidence_decay(self, value: str, stale_after_days: int = 365) -> dict[str, Any]:
        observations = [Observation.model_validate(x) for x in self.store.load()["observations"] if x["value"] == value]
        if not observations:
            raise KeyError(value)
        latest = max(_aware(o.observed_at) for o in observations)
        age_days = max(0, (datetime.now(timezone.utc)-latest).days)
        historical_confidence = min(1.0, 0.45 + 0.12 * len({o.source for o in observations}))
        decay = min(0.8, age_days / max(1, stale_after_days) * 0.25)
        current_confidence = max(0.05, historical_confidence - decay)
        return {"value": value, "last_observed": latest.isoformat(), "age_days": age_days, "historical_confidence": round(historical_confidence,4), "current_confidence": round(current_confidence,4), "stale": age_days > stale_after_days}

    def clusters(self) -> list[dict[str, Any]]:
        """Deterministically group observations by explicit lineage/acquisition/issuer/host hints."""
        data = self.store.load()
        buckets: dict[str, list[str]] = defaultdict(list)
        for raw in data["observations"]:
            obs = Observation.model_validate(raw)
            key = str(obs.metadata.get("acquisition") or obs.metadata.get("oauth_issuer") or obs.metadata.get("cluster") or "unclustered")
            buckets[key].append(obs.value)
        return [{"cluster": key, "values": sorted(set(values)), "count": len(set(values))} for key, values in sorted(buckets.items())]

    def acquisition_lineage(self) -> list[dict[str, Any]]:
        relationships = [Relationship.model_validate(x) for x in self.store.load()["relationships"]]
        return [{"from": r.source_value, "to": r.target_value, "relationship": r.relationship_type, "confidence": r.confidence, "evidence_ids": r.evidence_ids} for r in relationships if r.relationship_type.lower() in {"acquired_by", "former_brand_of", "subsidiary_of", "rebranded_to"}]

    def correlate(self) -> list[dict[str, Any]]:
        data = self.store.load()
        rels = [Relationship.model_validate(x) for x in data["relationships"]]
        return [
            {
                "source": r.source_value,
                "relationship": r.relationship_type,
                "target": r.target_value,
                "confidence": r.confidence,
                "evidence_ids": r.evidence_ids,
            }
            for r in rels
        ]
