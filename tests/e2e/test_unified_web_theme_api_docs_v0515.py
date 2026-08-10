from __future__ import annotations

from fastapi.testclient import TestClient

from fossilscope.api_all import create_app


def test_dashboard_and_api_reference_share_security_workspace_theme(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))

    dashboard = client.get("/")
    docs = client.get("/docs")
    assert dashboard.status_code == 200
    assert docs.status_code == 200

    for page in (dashboard.text, docs.text):
        assert "Sentinel Forge" in page
        assert "#0b0f14" in page
        assert "#121922" in page
        assert "#283544" in page
        assert "#5aa9b8" in page
        assert "Segoe UI Variable Text" in page
        assert "Aptos" in page
        assert "#0d110e" not in page
        assert "#151b15" not in page
        assert "fonts.googleapis.com" not in page
        assert "cdn.jsdelivr.net" not in page

    assert "FossilScope Dashboard" in dashboard.text
    assert "API Reference" in docs.text
    assert "Reference-only explorer" in docs.text
    assert "Security Workspace" in dashboard.text
    assert "Security Workspace" in docs.text


def test_api_reference_renders_complete_openapi_contract_without_try_it(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    script = client.get("/assets/api-docs.js")
    schema = client.get("/openapi.json")

    assert script.status_code == 200
    assert schema.status_code == 200
    js = script.text
    for renderer in ("renderParams", "renderBody", "renderResponses", "renderModels"):
        assert renderer in js
    assert "fetch('/openapi.json'" in js
    assert "Try it" not in js
    assert "fetch(rec.path" not in js

    spec = schema.json()
    assert "historical observations" in spec["info"]["description"].lower()
    paths = spec["paths"]
    documented = {
        "/api/timeline": "get",
        "/api/candidates": "get",
        "/api/lifecycle": "get",
        "/api/graph": "get",
        "/api/clusters": "get",
        "/api/time-travel": "get",
        "/api/resurrections": "get",
        "/api/confidence-v2": "get",
        "/api/search": "get",
        "/api/jobs": "get",
        "/api/jobs/events": "get",
        "/api/notebook": "get",
        "/api/evidence-lineage/{artifact_id}": "get",
        "/api/v1/analysis/lifecycle": "post",
        "/api/v1/analysis/reobservation/prioritize": "post",
        "/api/v1/analysis/reobservation/plan": "post",
        "/api/v1/analysis/reobservation/retry": "post",
        "/api/v1/analysis/evolution/diff": "post",
        "/api/v1/analysis/evolution/stale-references": "post",
        "/api/v1/capabilities": "get",
        "/api/v1/runtime-compatibility": "get",
    }
    for path, method in documented.items():
        operation = paths[path][method]
        assert operation.get("summary")
        assert operation.get("description")
        assert operation.get("responses")
        assert any(response.get("description") for response in operation["responses"].values())

    for path in (
        "/api/v1/analysis/lifecycle",
        "/api/v1/analysis/reobservation/prioritize",
        "/api/v1/analysis/reobservation/plan",
        "/api/v1/analysis/reobservation/retry",
        "/api/v1/analysis/evolution/diff",
        "/api/v1/analysis/evolution/stale-references",
    ):
        assert paths[path]["post"].get("requestBody")

    assert spec.get("components", {}).get("schemas")


def test_reported_catalog_http_500_regression_is_closed(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))

    console_catalog = client.get("/api/v1/console/catalog")
    workbench_catalog = client.get("/api/v1/workbench/catalog")
    workbench = client.get("/workbench")

    assert console_catalog.status_code == 200
    assert workbench_catalog.status_code == 200
    assert workbench.status_code == 200
    assert console_catalog.json()["commands"]
    assert workbench_catalog.json()["features"]
    assert workbench_catalog.json()["execution"]["user_supplied_argv"] is False
    assert "catalog HTTP 500" not in workbench.text
