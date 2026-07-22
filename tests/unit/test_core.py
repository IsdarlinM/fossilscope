from pathlib import Path
from datetime import datetime, timezone
from sric.workspace import Workspace
from fossilscope.core import FossilEngine
from fossilscope.models import Observation


def test_scoring_separates_historical_from_current(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "w")
    e = FossilEngine(ws.root)
    e.add_observation(
        Observation(
            observation_id="1",
            entity_type="api",
            value="api-v1.test",
            source="archive",
            last_seen=datetime(2021, 1, 1, tzinfo=timezone.utc),
            current_reachable=False,
            evidence_ids=["E1"],
        )
    )
    c = e.score()[0]
    assert c.status.value == "HYPOTHESIS"
    assert "current_reachability" in c.components
    assert c.counter_evidence


def test_mixed_naive_and_aware_datetimes_do_not_crash(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "mixed")
    engine = FossilEngine(ws.root)
    engine.add_observation(
        Observation(
            observation_id="naive",
            entity_type="api",
            value="api-v1.test",
            source="archive",
            last_seen=datetime(2022, 1, 1),
        )
    )
    engine.add_observation(
        Observation(
            observation_id="aware",
            entity_type="api",
            value="api-v1.test",
            source="sdk",
            observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            current_reference=True,
        )
    )
    assert engine.score()


def test_passive_artifact_extraction(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "extract")
    engine = FossilEngine(ws.root)
    artifact = tmp_path / "bundle.js"
    artifact.write_text(
        "fetch('https://api-v1.example.test/export'); const h='legacy.example.test';",
        encoding="utf-8",
    )
    count = engine.extract_artifact(artifact, "js_bundle")
    values = {x["value"] for x in engine.store.load()["observations"]}
    assert count >= 1
    assert "https://api-v1.example.test/export" in values
