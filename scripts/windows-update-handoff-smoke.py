from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from sric.updater import OfficialReleaseChannel

from fossilscope import __version__, windows_update


def main() -> int:
    """Exercise the real Windows post-exit handoff without network/channel mutation.

    This developer smoke substitutes only official-channel discovery/download so the
    process topology can be tested against the current checkout. Signature/channel
    verification remains covered separately by updater tests and production code.
    """

    if os.name != "nt":
        print("This handoff smoke is Windows-only.", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parents[1]
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.is_file():
        print("Run this smoke from a FossilScope source checkout.", file=sys.stderr)
        return 2

    test_home_raw = os.environ.get("FOSSILSCOPE_UPDATE_TEST_HOME")
    if not test_home_raw:
        print("FOSSILSCOPE_UPDATE_TEST_HOME is required.", file=sys.stderr)
        return 2
    test_home = Path(test_home_raw).resolve()
    test_home.mkdir(parents=True, exist_ok=True)

    channel = OfficialReleaseChannel(
        schema_version=1,
        product="fossilscope",
        repository="IsdarlinM/fossilscope",
        version=__version__,
        commit="a" * 40,
        rollback_version=None,
        rollback_commit=None,
    )

    original_load = windows_update.sric_updater._load_official_channel
    original_download = windows_update.sric_updater._download_official_archive

    def local_channel(product: str) -> OfficialReleaseChannel:
        if product != "fossilscope":
            raise RuntimeError(f"unexpected smoke product: {product}")
        return channel

    def local_source(**kwargs: object) -> Path:
        if kwargs.get("expected_product") != "fossilscope":
            raise RuntimeError("unexpected smoke product source")
        if kwargs.get("expected_version") != __version__:
            raise RuntimeError("unexpected smoke version source")
        return repo_root

    windows_update.sric_updater._load_official_channel = local_channel
    windows_update.sric_updater._download_official_archive = local_source
    try:
        payload = windows_update.stage_official_windows_update(
            current_version=__version__,
            force=True,
            platform_name="nt",
            home=test_home,
        )
    finally:
        windows_update.sric_updater._load_official_channel = original_load
        windows_update.sric_updater._download_official_archive = original_download

    required = {
        "same_version": True,
        "forced": True,
        "staged": True,
        "installed": False,
        "action": "FORCED_REINSTALL",
        "handoff": "WINDOWS_POST_EXIT",
    }
    for key, expected in required.items():
        if payload.get(key) != expected:
            raise RuntimeError(
                f"unexpected handoff smoke payload: {key}={payload.get(key)!r}, "
                f"expected {expected!r}"
            )

    print(json.dumps(payload, indent=2))
    print(f"RESULT_FILE={payload['result_file']}")
    print(
        "The Python staging process will now exit. The verified local wheel reinstall "
        "must finish in the background without opening another console window."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
