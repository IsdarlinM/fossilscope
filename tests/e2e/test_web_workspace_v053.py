from __future__ import annotations

from pathlib import Path

import pytest
import uvicorn
from typer.testing import CliRunner

import fossilscope.cli_more as cli_more
from fossilscope.api_all import create_app as create_complete_app
from fossilscope.cli_all import app
from sric.workspace import Workspace

runner = CliRunner()


def test_web_opens_named_workspace_and_uses_complete_factory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = Workspace.create(tmp_path, "imr")
    sentinel_app = object()
    calls: dict[str, object] = {}

    def fake_factory(path: Path) -> object:
        calls["factory_path"] = path
        return sentinel_app

    def fake_uvicorn_run(app_object: object, *, host: str, port: int) -> None:
        calls["app"] = app_object
        calls["host"] = host
        calls["port"] = port

    monkeypatch.setattr(cli_more, "create_complete_app", fake_factory)
    monkeypatch.setattr(uvicorn, "run", fake_uvicorn_run)

    result = runner.invoke(app, ["web", "imr", "--root", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert calls["factory_path"] == workspace.root.resolve()
    assert calls["app"] is sentinel_app
    assert calls["host"] == "127.0.0.1"
    assert calls["port"] == 8767
    assert "Traceback" not in result.output


def test_web_missing_workspace_is_actionable_and_has_no_traceback(tmp_path: Path) -> None:
    Workspace.create(tmp_path, "demo")

    result = runner.invoke(app, ["web", "imr", "--root", str(tmp_path)])

    assert result.exit_code == 2
    assert "Workspace 'imr' was not found" in result.output
    assert "Available workspaces: demo" in result.output
    assert "fossilscope init imr" in result.output
    assert "--root PATH" in result.output
    assert "Traceback" not in result.output


def test_web_rejects_path_like_workspace_names(tmp_path: Path) -> None:
    result = runner.invoke(app, ["web", "../outside", "--root", str(tmp_path)])

    assert result.exit_code == 2
    assert "Invalid workspace name" in result.output
    assert "Traceback" not in result.output


def test_web_rejects_workspace_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    Workspace.create(tmp_path, "outside")
    link = root / "imr"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")

    result = runner.invoke(app, ["web", "imr", "--root", str(root)])

    assert result.exit_code == 2
    assert "symlinks are not accepted" in result.output
    assert "Traceback" not in result.output


def test_complete_web_factory_exposes_vnext_and_capability_routes(tmp_path: Path) -> None:
    workspace = Workspace.create(tmp_path, "imr")
    web_app = create_complete_app(workspace.root)
    paths = {route.path for route in web_app.routes}

    assert "/api/v1/analysis/lifecycle" in paths
    assert "/api/v1/capabilities" in paths
