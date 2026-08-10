from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner
from sric.workspace import Workspace

import fossilscope.cli_more as cli_more
from fossilscope.cli_all import app
from fossilscope.core import FossilEngine

runner = CliRunner()


def _workspace(tmp_path: Path, name: str = "guarded") -> Path:
    root = tmp_path / "workspaces"
    workspace = Workspace.create(root, name)
    FossilEngine(workspace.root)
    return root


def test_every_registered_callback_has_product_exception_boundary() -> None:
    callbacks = [item.callback for item in app.registered_commands if item.callback is not None]
    assert callbacks
    assert all(getattr(callback, "_fossilscope_guarded", False) for callback in callbacks)


def test_graph_at_invalid_timestamp_is_controlled_without_traceback(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    result = runner.invoke(app, ["graph-at", "guarded", "--at", "not-a-date", "--root", str(root)])
    assert result.exit_code == 2
    assert "Operation rejected" in result.output
    assert "ValueError" in result.output
    assert "Traceback" not in result.output


def test_lifecycle_invalid_schema_is_specific_controlled_error(tmp_path: Path) -> None:
    fixture = tmp_path / "lifecycle.json"
    fixture.write_text('[{"unexpected": true}]', encoding="utf-8")
    result = runner.invoke(app, ["lifecycle-assess", str(fixture)])
    assert result.exit_code == 2
    assert "invalid lifecycle evidence" in result.output
    assert "Traceback" not in result.output


def test_reobserve_plan_invalid_schema_is_specific_controlled_error(tmp_path: Path) -> None:
    fixture = tmp_path / "plan.json"
    fixture.write_text('[{"unexpected": true}]', encoding="utf-8")
    result = runner.invoke(app, ["reobserve-plan", str(fixture)])
    assert result.exit_code == 2
    assert "invalid reobservation request" in result.output
    assert "Traceback" not in result.output


def test_reobserve_retry_invalid_schema_is_specific_controlled_error(tmp_path: Path) -> None:
    fixture = tmp_path / "retry.json"
    fixture.write_text('{"unexpected": true}', encoding="utf-8")
    result = runner.invoke(app, ["reobserve-retry", str(fixture)])
    assert result.exit_code == 2
    assert "invalid reobservation retry request" in result.output
    assert "Traceback" not in result.output


def test_report_write_failure_is_contained(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    output_directory = tmp_path / "report-directory"
    output_directory.mkdir()
    result = runner.invoke(
        app,
        ["report", "guarded", str(output_directory), "--root", str(root)],
    )
    assert result.exit_code == 2
    assert "Operation rejected" in result.output
    assert "Traceback" not in result.output


def test_unknown_job_id_is_contained(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    result = runner.invoke(app, ["jobs", "guarded", "--id", "missing-job", "--root", str(root)])
    assert result.exit_code == 2
    assert "Operation rejected" in result.output
    assert "Traceback" not in result.output


def test_unexpected_callback_error_is_redacted_and_never_escapes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _workspace(tmp_path)

    class BrokenEngine:
        def __init__(self, _path: Path) -> None:
            raise RuntimeError("token=super-secret-callback-value")

    monkeypatch.setattr(cli_more, "FossilEngine", BrokenEngine)
    result = runner.invoke(app, ["lifecycle", "guarded", "--root", str(root)])
    assert result.exit_code == 1
    assert "Operation failed safely" in result.output
    assert "RuntimeError" in result.output
    assert "super-secret-callback-value" not in result.output
    assert "Traceback" not in result.output
