from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typer.testing import CliRunner

import fossilscope.sric_bootstrap as bootstrap
from fossilscope.api_all import _mount_degraded_workbench
from fossilscope.cli_all import app, normalize_help_argv
from sric.web_console import build_command_catalog
from sric.web_workbench import build_feature_catalog, feature_contract


def _runtime(version: str, *, compatible: bool, missing: tuple[str, ...] = ()) -> bootstrap.SRICRuntimeStatus:
    return bootstrap.SRICRuntimeStatus(version, compatible, missing, (() if compatible else ("incompatible",)))


def test_stale_sric_without_current_web_runtime_is_rejected_before_web_import(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap.importlib.metadata, "version", lambda _name: "0.5.11")
    monkeypatch.setattr(
        bootstrap,
        "_find_module",
        lambda name: name in {"sric.web_console", "sric.web_workbench", "sric.web_catalog"},
    )
    result = bootstrap.status()
    assert result.compatible is False
    assert any("older than required 0.5.12" in reason for reason in result.reasons)


def test_055_and_056_bridge_then_057_advances_to_current_floor(monkeypatch: pytest.MonkeyPatch) -> None:
    states = iter(
        [
            _runtime("0.5.5", compatible=False),
            _runtime("0.5.7", compatible=False),
            _runtime("0.5.12", compatible=True),
        ]
    )
    bridges: list[str] = []
    updates: list[dict[str, object]] = []
    fake = SimpleNamespace(perform_product_update=lambda **kwargs: updates.append(kwargs))
    monkeypatch.setattr(bootstrap, "status", lambda: next(states))
    monkeypatch.setattr(bootstrap, "_upgrade_055_to_056", lambda: bridges.append("055-056"))
    monkeypatch.setattr(bootstrap, "_upgrade_056_to_057", lambda: bridges.append("056-057"))
    monkeypatch.setattr(bootstrap, "_updater", lambda: fake)
    monkeypatch.setattr(bootstrap, "_require_updater_api", lambda *_args: None)
    monkeypatch.setattr(bootstrap.importlib, "invalidate_caches", lambda: None)
    assert bootstrap.ensure_for_official_update().compatible is True
    assert bridges == ["055-056", "056-057"]
    assert updates == [
        {
            "expected_product": "sric-core",
            "current_version": "0.5.7",
            "check_only": False,
            "force": False,
        }
    ]


def test_same_version_missing_catalog_forces_repair(monkeypatch: pytest.MonkeyPatch) -> None:
    states = iter(
        [
            _runtime("0.5.12", compatible=False, missing=("sric.web_catalog",)),
            _runtime("0.5.12", compatible=True),
        ]
    )
    updates: list[dict[str, object]] = []
    fake = SimpleNamespace(perform_product_update=lambda **kwargs: updates.append(kwargs))
    monkeypatch.setattr(bootstrap, "status", lambda: next(states))
    monkeypatch.setattr(bootstrap, "_updater", lambda: fake)
    monkeypatch.setattr(bootstrap, "_require_updater_api", lambda *_args: None)
    monkeypatch.setattr(bootstrap.importlib, "invalidate_caches", lambda: None)
    bootstrap.ensure_for_official_update()
    assert updates == [
        {
            "expected_product": "sric-core",
            "current_version": "0.5.12",
            "check_only": False,
            "force": True,
        }
    ]


def test_degraded_workbench_reports_503_instead_of_killing_cli() -> None:
    degraded = FastAPI()
    _mount_degraded_workbench(degraded, "missing sric.web_workbench")
    client = TestClient(degraded)
    assert client.get("/workbench").status_code == 503
    coverage = client.get("/api/v1/workbench/coverage")
    assert coverage.status_code == 503
    assert coverage.json()["status"] == "RUNTIME_INCOMPATIBLE"


def test_every_fossilscope_command_and_argument_is_web_represented_and_all_help_forms() -> None:
    cli = build_command_catalog("fossilscope.cli_all")
    web = build_feature_catalog("fossilscope.cli_all")
    assert feature_contract("fossilscope.cli_all")["complete"] is True
    cli_by_path = {item["path"]: item for item in cli}
    web_by_path = {item["path"]: item for item in web}
    assert set(cli_by_path) == set(web_by_path)
    runner = CliRunner()
    for args in (["--help"], ["-h"], ["help"]):
        assert runner.invoke(app, args).exit_code == 0
    for path, command in cli_by_path.items():
        args = path.split()
        assert runner.invoke(app, [*args, "--help"]).exit_code == 0, path
        assert runner.invoke(app, [*args, "-h"]).exit_code == 0, path
        normalized = normalize_help_argv(["fossilscope", *args, "help"])
        assert normalized[-1] == "--help", path
        assert runner.invoke(app, normalized[1:]).exit_code == 0, path
        assert [p["name"] for p in command["params"]] == [p["name"] for p in web_by_path[path]["params"]]
