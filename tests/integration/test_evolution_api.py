import hashlib
from pathlib import Path

from fastapi.testclient import TestClient

from fossilscope.api_vnext import create_app


def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(tmp_path))


def observation(
    observation_id: str,
    version: str,
    when: str,
    *,
    endpoints: list[str] | None = None,
    references: list[str] | None = None,
    historical: bool = True,
) -> dict[str, object]:
    return {
        "observation_id": observation_id,
        "artifact_id": "sdk-one",
        "artifact_kind": "SDK",
        "version_label": version,
        "observed_at": when,
        "content_sha256": hashlib.sha256(observation_id.encode()).hexdigest(),
        "endpoints": endpoints or [],
        "references": references or [],
        "source_id": f"source-{observation_id}",
        "evidence_ids": [f"E-{observation_id}"],
        "historical": historical,
    }


def test_evolution_api_reports_changes_without_current_exposure_claim(tmp_path: Path) -> None:
    response = client(tmp_path).post(
        "/api/v1/analysis/evolution/diff",
        json={
            "observations": [
                observation("old", "1.0.0", "2025-01-01T00:00:00Z", endpoints=["/legacy", "/stable"]),
                observation("new", "2.0.0", "2025-02-01T00:00:00Z", endpoints=["/stable", "/v2"]),
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["deltas"][0]["removed_endpoints"] == ["/legacy"]
    assert payload["deltas"][0]["added_endpoints"] == ["/v2"]
    assert payload["current_exposure_proved"] is False
    assert payload["validated_findings_created"] == 0


def test_stale_reference_api_never_sends_requests(tmp_path: Path) -> None:
    response = client(tmp_path).post(
        "/api/v1/analysis/evolution/stale-references",
        json={
            "observations": [
                observation("old", "1.0.0", "2025-01-01T00:00:00Z", endpoints=["https://legacy.example/api"]),
                observation("new", "2.0.0", "2025-02-01T00:00:00Z"),
                observation(
                    "current-docs",
                    "current",
                    "2026-01-01T00:00:00Z",
                    references=["https://legacy.example/api"],
                    historical=False,
                ),
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["candidates"][0]["status"] == "HYPOTHESIS"
    assert payload["current_reachability_proved"] is False
    assert payload["requests_sent"] == 0
    assert payload["validated_findings_created"] == 0
