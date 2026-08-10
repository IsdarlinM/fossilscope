from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_windows_installer_never_mutates_existing_runtime_in_place() -> None:
    text = (ROOT / "scripts" / "install-windows.cmd").read_text(encoding="utf-8")
    assert 'set "VENV_ROLLBACK=%INSTALL_ROOT%\\venv.rollback"' in text
    assert 'move /y "%VENV%" "%VENV_ROLLBACK%"' in text
    assert 'rmdir /s /q "%VENV%"' in text
    assert 'move /y "%VENV_ROLLBACK%" "%VENV%"' in text
    assert 'rmdir /s /q "%INSTALL_ROOT%"' not in text
    assert "--force-reinstall" not in text


def test_windows_installer_detects_the_reported_dependency_corruption() -> None:
    text = (ROOT / "scripts" / "install-windows.cmd").read_text(encoding="utf-8")
    assert "import annotated_types, pydantic, fossilscope" in text
    assert "m.version('fossilscope') == '0.5.15'" in text
    assert "sric.web_security_workspace" in text
    assert "sric.web_theme" in text
    assert "(0,5,15)<=v<(0,6,0)" in text
    assert "pip check" in text
    assert "doctor --json" in text
    assert "capabilities" in text


def test_explicit_windows_repair_is_data_preserving_alias() -> None:
    text = (ROOT / "scripts" / "repair-windows.cmd").read_text(encoding="utf-8")
    assert "workspaces, configuration, evidence and reports are preserved" in text
    assert 'call "%SCRIPT_DIR%install-windows.cmd"' in text
    assert "rmdir" not in text.lower()
