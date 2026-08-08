from pathlib import Path

from fastapi.testclient import TestClient

from fossilscope.api_vnext import create_app


def test_reobservation_priority_api_is_passive_only(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.post(
        "/api/v1/analysis/reobservation/prioritize",
        json={
            "candidates": [
                {
                    "asset_id": "legacy-api",
                    "target": "https://legacy.example.test/api",
                    "exposure_state": "REACHABILITY_UNKNOWN",
                    "current_reference": True,
                    "auth_relevance": True,
                    "evidence_ids": ["ev-1"],
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["planned_request_count"] == 1
    assert payload["requests"][0]["mode"] == "PASSIVE"
    assert payload["passive_only"] is True
    assert payload["requests_sent"] == 0
