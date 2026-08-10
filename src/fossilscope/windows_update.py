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

        helper_source = Path(__file__).with_name("windows_update_helper.py")
        if not helper_source.is_file():
            raise RuntimeError("Windows update helper is missing from the FossilScope package")
        helper = staging / "apply_windows_update.py"
        shutil.copy2(helper_source, helper)

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
