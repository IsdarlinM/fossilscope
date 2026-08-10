from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import asdict
from email.parser import Parser
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


def _status_payload(
    status: Any,
    *,
    staged: bool,
    result_file: Path,
    force: bool,
) -> dict[str, object]:
    payload = dict(asdict(status))
    payload["forced"] = bool(force)
    payload["staged"] = staged
    payload["installed"] = False if staged else bool(payload.get("installed"))
    if staged:
        payload["handoff"] = "WINDOWS_POST_EXIT"
        payload["result_file"] = str(result_file)
        payload["action"] = (
            "FORCED_REINSTALL" if force and bool(payload.get("same_version")) else "UPDATE"
        )
    else:
        payload["action"] = "NONE"
    return payload


def _verify_built_wheel(wheel: Path, *, expected_version: str) -> None:
    if wheel.suffix.lower() != ".whl" or not wheel.is_file():
        raise RuntimeError("Windows update staging did not produce a wheel artifact")
    try:
        with zipfile.ZipFile(wheel) as archive:
            metadata_names = [
                name
                for name in archive.namelist()
                if name.endswith(".dist-info/METADATA")
            ]
            if len(metadata_names) != 1:
                raise RuntimeError("built wheel contains an invalid METADATA layout")
            metadata = Parser().parsestr(
                archive.read(metadata_names[0]).decode("utf-8", errors="strict")
            )
    except (OSError, UnicodeDecodeError, zipfile.BadZipFile) as exc:
        raise RuntimeError(f"cannot verify staged wheel metadata: {exc}") from exc

    if metadata.get("Name", "").strip().lower().replace("_", "-") != PRODUCT:
        raise RuntimeError("built wheel product metadata does not match FossilScope")
    if metadata.get("Version", "").strip() != expected_version:
        raise RuntimeError(
            "built wheel version metadata does not match the verified release channel"
        )


def _build_verified_wheel(
    source_archive: Path,
    *,
    expected_version: str,
    staging: Path,
    runtime_python: str,
    log_path: Path,
) -> Path:
    """Build a verified source snapshot before the active executable exits.

    The detached helper only installs prebuilt wheels. This avoids invoking build
    backends from a no-console child process, which could otherwise create visible
    console windows on Windows.
    """

    wheel_dir = staging / "wheels"
    wheel_dir.mkdir(parents=True, exist_ok=True)
    before = {item.resolve() for item in wheel_dir.glob("*.whl")}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", errors="replace") as log:
        log.write("$ prebuild verified FossilScope wheel\n")
        log.flush()
        subprocess.run(
            [
                runtime_python,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--no-build-isolation",
                "--disable-pip-version-check",
                "--wheel-dir",
                str(wheel_dir),
                str(source_archive),
            ],
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            shell=False,
            env={
                **os.environ,
                "SENTINEL_BANNER": "never",
                "NO_COLOR": "1",
                "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            },
        )

    produced = [
        item
        for item in wheel_dir.glob("*.whl")
        if item.resolve() not in before
    ]
    if len(produced) != 1:
        raise RuntimeError(
            f"expected exactly one FossilScope wheel from verified source; got {len(produced)}"
        )
    wheel = produced[0]
    _verify_built_wheel(wheel, expected_version=expected_version)
    return wheel


def _helper_creationflags() -> int:
    """Launch the post-exit helper without allocating another console window."""

    return (
        getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    )


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
        return _status_payload(
            status,
            staged=False,
            result_file=result_path,
            force=False,
        )

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

    root.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="sentinel-fossilscope-update-"))
    try:
        target_source = sric_updater._download_official_archive(
            repository=channel.repository,
            commit=channel.commit,
            expected_product=PRODUCT,
            expected_version=channel.version,
            destination=staging / f"{PRODUCT}-{channel.version}.zip",
        )
        target = _build_verified_wheel(
            target_source,
            expected_version=channel.version,
            staging=staging,
            runtime_python=sys.executable,
            log_path=log_path,
        )
        if same_version:
            rollback = target
        else:
            assert channel.rollback_commit is not None
            assert channel.rollback_version is not None
            rollback_source = sric_updater._download_official_archive(
                repository=channel.repository,
                commit=channel.rollback_commit,
                expected_product=PRODUCT,
                expected_version=channel.rollback_version,
                destination=staging
                / f"rollback-{PRODUCT}-{channel.rollback_version}.zip",
            )
            rollback = _build_verified_wheel(
                rollback_source,
                expected_version=channel.rollback_version,
                staging=staging,
                runtime_python=sys.executable,
                log_path=log_path,
            )

        helper_source = Path(__file__).with_name("windows_update_helper.py")
        if not helper_source.is_file():
            raise RuntimeError("Windows update helper is missing from the FossilScope package")
        helper = staging / "apply_windows_update.py"
        shutil.copy2(helper_source, helper)

        result_path.unlink(missing_ok=True)
        lock_path.write_text(
            json.dumps(
                {
                    "product": PRODUCT,
                    "parent_pid": os.getpid(),
                    "target_version": channel.version,
                    "forced": bool(force),
                    "action": "FORCED_REINSTALL" if same_version else "UPDATE",
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
        subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            creationflags=_helper_creationflags(),
        )
    except Exception:
        lock_path.unlink(missing_ok=True)
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return _status_payload(
        status,
        staged=True,
        result_file=result_path,
        force=force,
    )
