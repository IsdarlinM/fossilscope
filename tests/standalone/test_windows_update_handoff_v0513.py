from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fossilscope import cli_update
from fossilscope import windows_update
from fossilscope import windows_update_helper
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


def _fake_wheel(path: Path, version: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            f"fossilscope-{version}.dist-info/METADATA",
            f"Metadata-Version: 2.1\nName: fossilscope\nVersion: {version}\n",
        )
    return path


def test_same_version_force_is_staged_until_parent_exits(tmp_path: Path, monkeypatch) -> None:
    stage = tmp_path / "stage"
    captured: dict[str, object] = {"builds": []}

    def fake_mkdtemp(*, prefix: str) -> str:
        assert prefix == "sentinel-fossilscope-update-"
        stage.mkdir()
        return str(stage)

    def fake_download(**kwargs: object) -> Path:
        destination = Path(str(kwargs["destination"]))
        destination.write_bytes(b"verified archive fixture")
        return destination

    def fake_build(
        source_archive: Path,
        *,
        expected_version: str,
        staging: Path,
        runtime_python: str,
        log_path: Path,
    ) -> Path:
        assert source_archive.suffix == ".zip"
        assert runtime_python == sys.executable
        assert log_path.name == "update-handoff.log"
        builds = captured["builds"]
        assert isinstance(builds, list)
        builds.append((source_archive, expected_version))
        return _fake_wheel(
            staging / "wheels" / f"fossilscope-{expected_version}-py3-none-any.whl",
            expected_version,
        )

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
    monkeypatch.setattr(windows_update, "_build_verified_wheel", fake_build)
    monkeypatch.setattr(windows_update.subprocess, "Popen", fake_popen)

    payload = windows_update.stage_official_windows_update(
        current_version="0.5.13",
        force=True,
        platform_name="nt",
        home=tmp_path,
    )

    assert payload["staged"] is True
    assert payload["installed"] is False
    assert payload["forced"] is True
    assert payload["same_version"] is True
    assert payload["action"] == "FORCED_REINSTALL"
    assert payload["handoff"] == "WINDOWS_POST_EXIT"
    assert len(captured["builds"]) == 1

    command = captured["command"]
    assert isinstance(command, list)
    assert command[3] == sys.executable
    assert command[4] == command[5]
    assert Path(command[4]).suffix == ".whl"
    assert "apply_windows_update.py" in command[1]

    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    flags = int(kwargs["creationflags"])
    assert flags & 0x08000000
    assert not flags & 0x00000008
    assert kwargs["stdin"] is windows_update.subprocess.DEVNULL
    assert kwargs["stdout"] is windows_update.subprocess.DEVNULL
    assert kwargs["stderr"] is windows_update.subprocess.DEVNULL

    wrapper = (tmp_path / ".local" / "bin" / "fossilscope.cmd").read_text(
        encoding="utf-8"
    )
    assert "update-in-progress.json" in wrapper
    assert "venv\\Scripts\\fossilscope.exe" in wrapper
    lock = tmp_path / ".fossilscope" / "update-in-progress.json"
    assert lock.is_file()
    lock_text = lock.read_text(encoding="utf-8")
    assert '"forced": true' in lock_text.lower()
    assert '"action": "FORCED_REINSTALL"' in lock_text


def test_built_wheel_metadata_is_verified_before_handoff(tmp_path: Path) -> None:
    valid = _fake_wheel(tmp_path / "fossilscope-0.5.16-py3-none-any.whl", "0.5.16")
    windows_update._verify_built_wheel(valid, expected_version="0.5.16")

    with pytest.raises(RuntimeError, match="version metadata"):
        windows_update._verify_built_wheel(valid, expected_version="0.5.17")


def test_helper_preserves_force_action_from_lock(tmp_path: Path) -> None:
    lock = tmp_path / "update-in-progress.json"
    lock.write_text(
        '{"forced": true, "action": "FORCED_REINSTALL"}',
        encoding="utf-8",
    )
    assert windows_update_helper._lock_evidence(lock) == (
        True,
        "FORCED_REINSTALL",
    )

    lock.write_text("not-json", encoding="utf-8")
    assert windows_update_helper._lock_evidence(lock) == (False, "UNKNOWN")


def test_helper_waits_before_mutating_and_verifies_runtime_plus_complete_web_contract() -> None:
    helper = Path(windows_update.__file__).with_name("windows_update_helper.py")
    source = helper.read_text(encoding="utf-8")
    wheel_guard_position = source.index("_require_prebuilt_wheel(target_archive")
    wait_position = source.index("wait_for_parent(int(parent_pid))")
    pip_position = source.index('"pip",\n            "install"')
    assert wheel_guard_position < wait_position < pip_position
    assert "OpenProcess.restype = ctypes.c_void_p" in source
    assert "artifact must be a prebuilt wheel" in source
    assert "creationflags=_hidden_creationflags()" in source
    assert "forced, action = _lock_evidence(lock)" in source
    assert '"forced": forced' in source
    assert '"action": action' in source
    assert "import annotated_types, pydantic, fossilscope, sric.web_guardrails" in source
    assert "install_json_safe_catalog()" in source
    assert "build_json_safe_command_catalog('fossilscope.cli_all')" in source
    assert "build_feature_catalog('fossilscope.cli_all')" in source
    assert "feature_contract('fossilscope.cli_all')" in source
    assert "len(catalog)==len(features)" in source
    assert "contract.get('complete') is True" in source
    assert '[runtime_python, "-m", "pip", "check"]' in source
    assert "--force-reinstall" in source
    assert windows_update_helper._hidden_creationflags("nt") & 0x08000000
    assert windows_update_helper._hidden_creationflags("posix") == 0


def test_cli_routes_official_windows_force_reinstall_to_silent_handoff(monkeypatch) -> None:
    monkeypatch.setattr(cli_update, "_is_windows", lambda: True)
    monkeypatch.setattr(cli_update, "ensure_for_official_update", lambda: None)
    monkeypatch.setattr(
        cli_update,
        "stage_official_windows_update",
        lambda **_kwargs: {
            "current_version": "0.5.13",
            "available_version": "0.5.13",
            "product": "fossilscope",
            "same_version": True,
            "forced": True,
            "action": "FORCED_REINSTALL",
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
    assert '"forced": true' in result.output.lower()
    assert '"action": "FORCED_REINSTALL"' in result.output
    assert "verified same-version reinstall staged for windows" in result.output.lower()
    assert "without opening additional console windows" in result.output.lower()
