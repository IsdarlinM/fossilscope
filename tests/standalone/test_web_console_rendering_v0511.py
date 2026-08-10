from __future__ import annotations

from fastapi.testclient import TestClient

from fossilscope.api_all import create_app


def test_legacy_console_is_alias_and_guided_workbench_is_reachable(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))

    page = client.get("/console")
    assert page.status_code == 200
    assert "Security Console" in page.text
    assert "command-oriented console has been retired" in page.text
    assert "Command Console" not in page.text
    assert "Advanced argv" not in page.text
    assert "Additional arguments" not in page.text
    csp = page.headers["content-security-policy"]
    assert "script-src 'self'" in csp
    assert "style-src 'self' 'unsafe-inline'" in csp

    styles = client.get("/console/styles.css")
    assert styles.status_code == 200
    assert styles.headers["content-type"].startswith("text/css")

    script = client.get("/console/app.js")
    assert script.status_code == 200
    assert "application/javascript" in script.headers["content-type"]
    assert '/workbench' in script.text

    catalog = client.get("/api/v1/console/catalog")
    assert catalog.status_code == 200
    commands = catalog.json()["commands"]
    assert commands
    assert any(item["path"] == "doctor" for item in commands)

    workbench = client.get("/workbench")
    assert workbench.status_code == 200
    assert "No command syntax is required" in workbench.text
    feature_catalog = client.get("/api/v1/workbench/catalog")
    assert feature_catalog.status_code == 200
    payload = feature_catalog.json()
    assert payload["features"]
    assert payload["execution"]["user_supplied_argv"] is False
    coverage = client.get("/api/v1/workbench/coverage")
    assert coverage.status_code == 200
    assert coverage.json()["complete"] is True
