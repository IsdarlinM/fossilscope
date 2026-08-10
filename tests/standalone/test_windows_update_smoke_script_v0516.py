from __future__ import annotations

from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_windows_handoff_smoke_python_is_local_only_and_compiles() -> None:
    source = (_root() / "scripts" / "windows-update-handoff-smoke.py").read_text(
        encoding="utf-8"
    )
    compile(source, "windows-update-handoff-smoke.py", "exec")
    assert "stage_official_windows_update(" in source
    assert "force=True" in source
    assert 'home=test_home' in source
    assert "_load_official_channel = local_channel" in source
    assert "_download_official_archive = local_source" in source
    assert 'return repo_root' in source
    assert "urlopen" not in source
    assert "requests." not in source
    assert '"FORCED_REINSTALL"' in source
    assert '"WINDOWS_POST_EXIT"' in source


def test_windows_handoff_smoke_cmd_uses_isolated_runtime_and_checks_result() -> None:
    source = (_root() / "scripts" / "test-windows-update-handoff.cmd").read_text(
        encoding="utf-8"
    )
    lowered = source.lower()
    assert "%userprofile%\\.fossilscope\\venv\\scripts\\python.exe" in lowered
    assert "%temp%\\fossilscope-update-handoff-smoke" in lowered
    assert "windows-update-handoff-smoke.py" in lowered
    assert "update-result.json" in lowered
    assert "update-in-progress.json" in lowered
    assert "status')=='installed'" in lowered
    assert "d.get('forced') is true" in lowered
    assert "d.get('action')=='forced_reinstall'" in lowered
    assert "stale update lock remains" in lowered
    assert "taskkill" not in lowered
    assert "powershell" not in lowered
