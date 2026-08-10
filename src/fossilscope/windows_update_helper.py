from __future__ import annotations

import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def wait_for_parent(pid: int, timeout_ms: int = 300000) -> None:
    """Wait for a Windows process handle without truncating it on 64-bit systems."""
    synchronize = 0x00100000
    wait_object_0 = 0x00000000
    wait_timeout = 0x00000102
    kernel32 = ctypes.windll.kernel32
    kernel32.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    kernel32.WaitForSingleObject.restype = ctypes.c_ulong
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_int

    handle = kernel32.OpenProcess(synchronize, False, pid)
    if not handle:
        time.sleep(1.0)
        return
    try:
        result = kernel32.WaitForSingleObject(handle, timeout_ms)
        if result == wait_timeout:
            raise RuntimeError("timed out waiting for the active FossilScope process to exit")
        if result != wait_object_0:
            raise RuntimeError(f"unexpected Windows wait result: {result}")
    finally:
        kernel32.CloseHandle(handle)


def run_logged(command: list[str], log_path: Path) -> None:
    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        log.write("$ " + subprocess.list2cmdline(command) + "\n")
        log.flush()
        subprocess.run(
            command,
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            shell=False,
            env={**os.environ, "SENTINEL_BANNER": "never", "NO_COLOR": "1"},
        )


def verify(runtime_python: str, expected_version: str, log_path: Path) -> None:
    probe = (
        "import importlib.metadata as m; "
        "assert m.version('fossilscope') == " + repr(expected_version) + "; "
        "import annotated_types, pydantic, fossilscope, sric.web_guardrails; "
        "from sric.web_catalog import build_json_safe_command_catalog, install_json_safe_catalog; "
        "install_json_safe_catalog(); "
        "from sric.web_workbench import build_feature_catalog, feature_contract; "
        "catalog=build_json_safe_command_catalog('fossilscope.cli_all'); "
        "features=build_feature_catalog('fossilscope.cli_all'); "
        "contract=feature_contract('fossilscope.cli_all'); "
        "assert catalog and len(catalog)==len(features) and contract.get('complete') is True; "
        "assert any(item.get('path') == 'doctor' for item in catalog); "
        "print(m.version('fossilscope'), m.version('sric-core'), len(catalog))"
    )
    run_logged([runtime_python, "-c", probe], log_path)
    run_logged([runtime_python, "-m", "pip", "check"], log_path)


def main() -> int:
    (
        _script,
        parent_pid,
        runtime_python,
        target_archive,
        rollback_archive,
        target_version,
        rollback_version,
        lock_path,
        result_path,
        log_path,
        staging_root,
    ) = sys.argv
    lock = Path(lock_path)
    result = Path(result_path)
    log = Path(log_path)
    staging = Path(staging_root)
    payload: dict[str, object] = {
        "product": "fossilscope",
        "target_version": target_version,
        "status": "FAILED",
        "rollback_attempted": False,
        "rollback_succeeded": False,
    }
    try:
        wait_for_parent(int(parent_pid))
        install = [
            runtime_python,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--no-deps",
            "--force-reinstall",
            target_archive,
        ]
        run_logged(install, log)
        verify(runtime_python, target_version, log)
        payload["status"] = "INSTALLED"
        payload["installed"] = True
    except Exception as exc:
        payload["error"] = f"{type(exc).__name__}: {exc}"
        if rollback_archive:
            payload["rollback_attempted"] = True
            try:
                rollback = [
                    runtime_python,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "--no-deps",
                    "--force-reinstall",
                    rollback_archive,
                ]
                run_logged(rollback, log)
                verify(runtime_python, rollback_version, log)
                payload["rollback_succeeded"] = True
                payload["status"] = "ROLLED_BACK"
            except Exception as rollback_exc:
                payload["rollback_error"] = (
                    f"{type(rollback_exc).__name__}: {rollback_exc}"
                )
                payload["status"] = "ROLLBACK_FAILED"
    finally:
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        try:
            lock.unlink(missing_ok=True)
        finally:
            try:
                shutil.rmtree(staging)
            except OSError:
                pass
    return 0 if payload["status"] == "INSTALLED" else 6


if __name__ == "__main__":
    raise SystemExit(main())
