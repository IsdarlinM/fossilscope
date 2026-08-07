from fastapi.testclient import TestClient

from fossilscope.api_vnext import create_app


def test_lifecycle_api_preserves_historical_current_separation() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/lifecycle",
        json={
            "evidence": [
                {
                    "evidence_id": "E-HIST",
                    "asset_id": "asset-1",
                    "kind": "HISTORICAL_REFERENCE",
                    "source_id": "archive",
                }
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["assessments"][0]["lifecycle"] == "HISTORICAL_ONLY"
    assert payload["historical_evidence_proves_current_exposure"] is False
    assert payload["validated_findings_created"] == 0


def test_reobservation_api_never_executes_requests() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/reobservation/plan",
        json={
            "requests": [
                {
                    "request_id": "R-1",
                    "asset_id": "asset-1",
                    "target": "api.example.test",
                    "reason": "CURRENT_STATE_UNKNOWN",
                    "mode": "PASSIVE",
                }
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["executed"] is False
    assert payload["requests_sent"] == 0
    assert payload["decisions"][0]["executable"] is True
