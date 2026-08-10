from fastapi.testclient import TestClient
from sric.workspace import Workspace

from fossilscope.api_all import create_app


def test_invalid_time_travel_timestamp_is_422(tmp_path) -> None:
    workspace = Workspace.create(tmp_path, "invalid-time")
    client = TestClient(create_app(workspace.root))
    response = client.get("/api/time-travel", params={"at": "not-a-date"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INPUT"


def test_missing_confidence_entity_is_404(tmp_path) -> None:
    workspace = Workspace.create(tmp_path, "missing-confidence")
    client = TestClient(create_app(workspace.root))
    response = client.get(
        "/api/confidence-v2",
        params={"value": "does-not-exist", "stale_after_days": 90},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
