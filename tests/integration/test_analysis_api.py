from datetime import datetime

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


def test_active_reobservation_without_approval_is_blocked_not_executed() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/reobservation/plan",
        json={
            "requests": [
                {
                    "request_id": "R-ACTIVE",
                    "asset_id": "asset-1",
                    "target": "https://api.example.test/health",
                    "reason": "CURRENT_STATE_UNKNOWN",
                    "mode": "ACTIVE_HTTPS",
                    "allow_patterns": ["api.example.test"],
                    "terms_acknowledged": True,
                    "human_approved": False,
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["executed"] is False
    assert payload["requests_sent"] == 0
    assert payload["decisions"][0]["executable"] is False
    assert "human approval" in " ".join(payload["decisions"][0]["blockers"])


def test_retry_api_rejects_invalid_delay_bounds_without_500() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/reobservation/retry",
        json={
            "request": {
                "request_id": "R-1",
                "asset_id": "asset-1",
                "target": "api.example.test",
                "reason": "CURRENT_STATE_UNKNOWN",
                "mode": "PASSIVE",
            },
            "base_delay_seconds": 120,
            "maximum_delay_seconds": 60,
        },
    )
    assert response.status_code == 422


def test_reobservation_api_rejects_naive_not_before_without_500() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/reobservation/plan",
        json={
            "requests": [
                {
                    "request_id": "R-NAIVE",
                    "asset_id": "asset-1",
                    "target": "api.example.test",
                    "reason": "CURRENT_STATE_UNKNOWN",
                    "mode": "PASSIVE",
                    "not_before": datetime(2026, 1, 1).isoformat(),
                }
            ]
        },
    )
    assert response.status_code == 422
