from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sric import updater as sric_updater

PRODUCT = "fossilscope"

HELPER_SOURCE = r"""from __future__ import annotations

import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


def wait_for_parent(pid: int, timeout_ms: int = 300000) -> None:
    SYNCHRONIZE = 0x00100000
    WAIT_OBJECT_0 = 0x00000000
    WAIT_TIMEOUT = 0x00000102
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
    if not handle:
        time.sleep(1.0)
        return
    try:
        result = kernel32.WaitForSingleObject(handle, timeout_ms)
        if result == WAIT_TIMEOUT:
            raise RuntimeError("timed out waiting for the active FossilScope process to exit")
        if result != WAIT_OBJECT_0:
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
        "import annotated_types, pydantic, fossilscope; "
        "print(m.version('fossilscope'))"
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
"""


def _wrapper_text() -> str:
    return r"""@echo off
setlocal EnableExtensions
set "INSTALL_ROOT=%USERPROFILE%\.fossilscope"
set "UPDATE_LOCK=%INSTALL_ROOT%\update-in-progress.json"
if exist "%UPDATE_LOCK%" (
  echo FossilScope update is finishing. Waiting for the verified handoff...
  for /L %%N in (1,1,300) do (
    if not exist "%UPDATE_LOCK%" goto :run
    >nul 2>&1 ping 127.0.0.1 -n 2
  )
  echo FossilScope update did not finish within 5 minutes.
  echo Review "%INSTALL_ROOT%\update-handoff.log" and "%INSTALL_ROOT%\update-result.json".
  exit /b 6
)
:run
@"%INSTALL_ROOT%\venv\Scripts\fossilscope.exe" %*
"""


def _status_payload(status: Any, *, staged: bool, result_file: Path) -> dict[str, object]:
    payload = dict(asdict(status))
    payload["staged"] = staged
    payload["installed"] = False if staged else bool(payload.get("installed"))
    if staged:
        payload["handoff"] = "WINDOWS_POST_EXIT"
        payload["result_file"] = str(result_file)
    return payload


def stage_official_windows_update(
    *,
    current_version: str,
    force: bool,
    platform_name: str | None = None,
    home: Path | None = None,
) -> dict[str, object]:
    """Stage a verified official update and apply it only after this process exits."""
    platform_value = os.name if platform_name is None else platform_name
    if platform_value != "nt":
        raise RuntimeError("Windows update handoff is only available on Windows")

    user_home = home or Path.home()
    root = user_home / ".fossilscope"
    bin_dir = user_home / ".local" / "bin"
    wrapper_path = bin_dir / "fossilscope.cmd"
    lock_path = root / "update-in-progress.json"
    result_path = root / "update-result.json"
    log_path = root / "update-handoff.log"

    channel = sric_updater._load_official_channel(PRODUCT)
    status = sric_updater.check_official_update(channel, current_version)
    comparison = sric_updater._compare_semver(channel.version, current_version)

    if force and comparison < 0:
        raise ValueError(
            "forced update does not permit downgrades; use the explicit rollback/recovery workflow"
        )
    if not status.update_available and not force:
        return _status_payload(status, staged=False, result_file=result_path)

    same_version = force and status.same_version
    rollback_version = channel.version if same_version else current_version
    if not same_version:
        if channel.rollback_version is None or channel.rollback_commit is None:
            raise ValueError(
                "official upgrades require rollback_version and rollback_commit metadata"
            )
        if channel.rollback_version != current_version:
            raise ValueError(
                "official rollback metadata does not match the currently installed version"
            )

    staging = Path(tempfile.mkdtemp(prefix="sentinel-fossilscope-update-"))
    try:
        target = sric_updater._download_official_archive(
            repository=channel.repository,
            commit=channel.commit,
            expected_product=PRODUCT,
            expected_version=channel.version,
            destination=staging / f"{PRODUCT}-{channel.version}.zip",
        )
        if same_version:
            rollback = target
        else:
            assert channel.rollback_commit is not None
            assert channel.rollback_version is not None
            rollback = sric_updater._download_official_archive(
                repository=channel.repository,
                commit=channel.rollback_commit,
                expected_product=PRODUCT,
                expected_version=channel.rollback_version,
                destination=staging
                / f"rollback-{PRODUCT}-{channel.rollback_version}.zip",
            )

        helper = staging / "apply_windows_update.py"
        helper.write_text(HELPER_SOURCE, encoding="utf-8")

        root.mkdir(parents=True, exist_ok=True)
        bin_dir.mkdir(parents=True, exist_ok=True)
        result_path.unlink(missing_ok=True)
        lock_path.write_text(
            json.dumps(
                {
                    "product": PRODUCT,
                    "parent_pid": os.getpid(),
                    "target_version": channel.version,
                    "started_at": time.time(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        tmp_wrapper = wrapper_path.with_suffix(".cmd.tmp")
        tmp_wrapper.write_text(_wrapper_text(), encoding="utf-8", newline="\r\n")
        os.replace(tmp_wrapper, wrapper_path)

        base_python = getattr(sys, "_base_executable", None) or sys.executable
        command = [
            str(base_python),
            str(helper),
            str(os.getpid()),
            sys.executable,
            str(target),
            str(rollback),
            channel.version,
            rollback_version,
            str(lock_path),
            str(result_path),
            str(log_path),
            str(staging),
        ]
        creationflags = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
            | getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        )
        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            creationflags=creationflags,
        )
    except Exception:
        lock_path.unlink(missing_ok=True)
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return _status_payload(status, staged=True, result_file=result_path)
