from fastapi.testclient import TestClient
from sric.workspace import Workspace

from fossilscope.api_all import create_app


def test_api_docs_are_same_origin_and_loadable_under_csp(tmp_path) -> None:
    workspace = Workspace.create(tmp_path, "docs")
    client = TestClient(create_app(workspace.root))
    response = client.get("/docs")
    assert response.status_code == 200
    assert "cdn.jsdelivr.net" not in response.text
    assert "/assets/api-docs.js" in response.text
    script = client.get("/assets/api-docs.js")
    assert script.status_code == 200
    assert "fetch('/openapi.json'" in script.text
    assert "script-src 'self'" in response.headers["content-security-policy"]
