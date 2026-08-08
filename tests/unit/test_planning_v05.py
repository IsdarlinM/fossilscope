from __future__ import annotations

from pathlib import Path

import pytest

import fossilscope.core as core
from fossilscope.core import FossilEngine
from fossilscope.planning import (
    CurrentExposureState,
    ReobservationCandidate,
    plan_reobservation,
)
from fossilscope.reobservation import ReobservationMode, ReobservationReason
from sric.workspace import Workspace


def test_import_json_uses_bounded_safe_loader(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = Workspace.create(tmp_path, "w")
    engine = FossilEngine(workspace.root)
    path = tmp_path / "too-large.json"
    path.write_text("{}" + " " * 32, encoding="utf-8")
    monkeypatch.setattr(core, "MAX_IMPORT_BYTES", 8)
    with pytest.raises(ValueError, match="import exceeds"):
        engine.import_json(path)


def test_planner_is_passive_first_and_prioritizes_unknown_current_state() -> None:
    plans = plan_reobservation(
        [
            ReobservationCandidate(
                asset_id="legacy-api",
                target="https://legacy.example.test/api",
                exposure_state=CurrentExposureState.REACHABILITY_UNKNOWN,
                current_reference=True,
                auth_relevance=True,
                evidence_ids=["ev-1"],
            ),
            ReobservationCandidate(
                asset_id="old-doc",
                target="https://docs.example.test/old",
                exposure_state=CurrentExposureState.HISTORICAL_ONLY,
                age_days=900,
            ),
        ]
    )
    assert plans[0].asset_id == "legacy-api"
    assert plans[0].mode is ReobservationMode.PASSIVE
    assert plans[0].reason is ReobservationReason.CURRENT_STATE_UNKNOWN
    assert all(plan.mode is ReobservationMode.PASSIVE for plan in plans)
