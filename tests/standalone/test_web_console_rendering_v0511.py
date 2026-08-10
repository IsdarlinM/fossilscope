from __future__ import annotations

from fastapi.testclient import TestClient

from fossilscope.api_all import create_app


def test_console_assets_catalog_and_workbench_are_reachable(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))

    page = client.get("/console")
    assert page.status_code == 200
    assert "FossilScope Command Console" in page.text
    csp = page.headers["content-security-policy"]
    assert "script-src 'self'" in csp
    assert "style-src 'self' 'unsafe-inline'" in csp

    styles = client.get("/console/styles.css")
    assert styles.status_code == 200
    assert styles.headers["content-type"].startswith("text/css")
    assert ".layout" in styles.text

    script = client.get("/console/app.js")
    assert script.status_code == 200
    assert "application/javascript" in script.headers["content-type"]

    catalog = client.get("/api/v1/console/catalog")
    assert catalog.status_code == 200
    commands = catalog.json()["commands"]
    assert commands
    assert any(item["path"] == "doctor" for item in commands)

    workbench = client.get("/workbench")
    assert workbench.status_code == 200
    feature_catalog = client.get("/api/v1/workbench/catalog")
    assert feature_catalog.status_code == 200
    assert feature_catalog.json()["features"]
    coverage = client.get("/api/v1/workbench/coverage")
    assert coverage.status_code == 200
    assert coverage.json()["complete"] is True
