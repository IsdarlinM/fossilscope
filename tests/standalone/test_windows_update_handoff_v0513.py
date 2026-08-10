from __future__ import annotations

import sys
from pathlib import Path

from typer.testing import CliRunner

from fossilscope import cli_update
from fossilscope import windows_update
from fossilscope.cli_all import app
from sric.updater import OfficialReleaseChannel


runner = CliRunner()


def _channel() -> OfficialReleaseChannel:
    return OfficialReleaseChannel(
        schema_version=1,
        product="fossilscope",
        repository="IsdarlinM/fossilscope",
        version="0.5.13",
        commit="a" * 40,
        rollback_version="0.5.12",
        rollback_commit="b" * 40,
    )


def test_same_version_force_is_staged_until_parent_exits(tmp_path: Path, monkeypatch) -> None:
    stage = tmp_path / "stage"
    captured: dict[str, object] = {}

    def fake_mkdtemp(*, prefix: str) -> str:
        assert prefix == "sentinel-fossilscope-update-"
        stage.mkdir()
        return str(stage)

    def fake_download(**kwargs: object) -> Path:
        destination = Path(str(kwargs["destination"]))
        destination.write_bytes(b"verified archive fixture")
        return destination

    def fake_popen(command: list[str], **kwargs: object) -> object:
        captured["command"] = command
        captured["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(windows_update.tempfile, "mkdtemp", fake_mkdtemp)
    monkeypatch.setattr(
        windows_update.sric_updater,
        "_load_official_channel",
        lambda _product: _channel(),
    )
    monkeypatch.setattr(
        windows_update.sric_updater,
        "_download_official_archive",
        fake_download,
    )
    monkeypatch.setattr(windows_update.subprocess, "Popen", fake_popen)

    payload = windows_update.stage_official_windows_update(
        current_version="0.5.13",
        force=True,
        platform_name="nt",
        home=tmp_path,
    )

    assert payload["staged"] is True
    assert payload["installed"] is False
    assert payload["handoff"] == "WINDOWS_POST_EXIT"
    command = captured["command"]
    assert isinstance(command, list)
    assert command[3] == sys.executable
    assert command[4] == command[5]
    assert "apply_windows_update.py" in command[1]

    wrapper = (tmp_path / ".local" / "bin" / "fossilscope.cmd").read_text(
        encoding="utf-8"
    )
    assert "update-in-progress.json" in wrapper
    assert "venv\\Scripts\\fossilscope.exe" in wrapper
    assert (tmp_path / ".fossilscope" / "update-in-progress.json").is_file()


def test_helper_waits_before_mutating_the_live_runtime() -> None:
    source = windows_update.HELPER_SOURCE
    wait_position = source.index("wait_for_parent(int(parent_pid))")
    pip_position = source.index('"pip",\n            "install"')
    assert wait_position < pip_position
    assert "import annotated_types, pydantic, fossilscope" in source
    assert '[runtime_python, "-m", "pip", "check"]' in source
    assert "--force-reinstall" in source


def test_cli_routes_official_windows_update_to_handoff(monkeypatch) -> None:
    monkeypatch.setattr(cli_update.os, "name", "nt")
    monkeypatch.setattr(cli_update, "ensure_for_official_update", lambda: None)
    monkeypatch.setattr(
        cli_update,
        "stage_official_windows_update",
        lambda **_kwargs: {
            "current_version": "0.5.13",
            "available_version": "0.5.13",
            "product": "fossilscope",
            "staged": True,
            "installed": False,
            "result_file": "C:/temp/update-result.json",
        },
    )

    def forbidden_in_process_update(**_kwargs: object) -> object:
        raise AssertionError("official Windows update must not run pip in the active process")

    monkeypatch.setattr(cli_update, "perform_product_update", forbidden_in_process_update)
    result = runner.invoke(app, ["update", "--force"])
    assert result.exit_code == 0
    assert '"staged": true' in result.output.lower()
    assert "will be applied after this FossilScope process exits" in result.output
