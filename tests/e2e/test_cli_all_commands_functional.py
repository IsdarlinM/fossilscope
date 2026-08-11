from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from typer.main import get_command
from typer.testing import CliRunner

import fossilscope.cli_update as cli_update
from fossilscope.cli_all import app
from fossilscope.collector_runtime import PassiveHTTPSCollectorRuntime
from sric.updater import UpdateCheck


runner = CliRunner()

EXPECTED_PUBLIC_COMMANDS = {
    "acquisitions",
    "add",
    "ai",
    "api-diff",
    "capabilities",
    "clusters",
    "collect",
    "collect-url",
    "confidence",
    "confidence-v2",
    "config",
    "correlate",
    "demo",
    "diff",
    "doctor",
    "evidence",
    "evidence-lineage",
    "evolution-diff",
    "export",
    "extract",
    "fossils",
    "graph-at",
    "help",
    "import",
    "init",
    "jobs",
    "lifecycle",
    "lifecycle-assess",
    "mobile-archaeology",
    "notebook",
    "plugins",
    "query",
    "reobservation-priority",
    "reobserve-plan",
    "reobserve-retry",
    "report",
    "resurrections",
    "scope",
    "stale-references",
    "time-travel",
    "timeline",
    "update",
    "validate",
    "version",
    "web",
    "workspace",
}


def _invoke(args: list[str], *, expected: int = 0) -> str:
    result = runner.invoke(app, args)
    assert result.exit_code == expected, f"{' '.join(args)} => {result.exit_code}\n{result.output}"
    assert "Traceback" not in result.output, f"{' '.join(args)} emitted traceback"
    return result.output


def test_every_public_command_has_a_functional_offline_smoke(tmp_path: Path, monkeypatch) -> None:
    """Execute every public command against deterministic local fixtures.

    The command set assertion is intentional: adding a command without extending this
    functional smoke is a release-gate failure. Network/server side effects are replaced
    with deterministic fakes while Scope/Policy and normal command parsing remain real.
    """

    registered = set(get_command(app).commands)
    assert registered == EXPECTED_PUBLIC_COMMANDS, (
        "Public CLI changed without functional smoke coverage. "
        f"missing_tests={sorted(registered - EXPECTED_PUBLIC_COMMANDS)} "
        f"stale_tests={sorted(EXPECTED_PUBLIC_COMMANDS - registered)}"
    )

    root = tmp_path / "workspaces"
    workspace = "smoke"
    root_arg = ["--root", str(root)]

    _invoke(["version"])
    _invoke(["doctor", "--json"])
    _invoke(["capabilities"])
    _invoke(["help"])
    _invoke(["init", workspace, *root_arg])
    _invoke(["workspace", "list", *root_arg])
    _invoke(["workspace", "show", workspace, *root_arg])
    _invoke(["config", "show", "--workspace", workspace, *root_arg])
    _invoke(["config", "explain", "telemetry", "--workspace", workspace, *root_arg])

    value = "https://legacy.example.test/v1"
    _invoke(
        [
            "add",
            workspace,
            "obs-1",
            "api_endpoint",
            value,
            "archive",
            "--last-seen",
            "2022-01-01",
            "--evidence",
            "E-ADD",
            *root_arg,
        ]
    )

    imported = tmp_path / "observations.json"
    imported.write_text(
        json.dumps(
            [
                {
                    "observation_id": "obs-2",
                    "entity_type": "api_endpoint",
                    "value": value,
                    "source": "sdk",
                    "current_reachable": True,
                    "current_reference": True,
                    "evidence_ids": ["E-IMPORT"],
                }
            ]
        ),
        encoding="utf-8",
    )
    _invoke(["import", workspace, str(imported), *root_arg])

    _invoke(["collect"])
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("See https://legacy.example.test/v1 and docs.example.test", encoding="utf-8")
    _invoke(["extract", workspace, str(artifact), *root_arg])
    _invoke(["timeline", workspace, *root_arg])
    _invoke(["diff", workspace, "2020-01-01", "2030-01-01", *root_arg])
    _invoke(["fossils", workspace, *root_arg])
    _invoke(["correlate", workspace, *root_arg])
    _invoke(["validate", workspace, "FSL-0001", "--evidence", "E-VALIDATE", "--confirm", *root_arg])

    exported = tmp_path / "export.json"
    _invoke(["export", workspace, str(exported), *root_arg])
    assert exported.is_file()
    _invoke(["lifecycle", workspace, *root_arg])
    _invoke(["graph-at", workspace, "--at", "2026-08-10T00:00:00+00:00", *root_arg])

    before = tmp_path / "before-openapi.json"
    after = tmp_path / "after-openapi.json"
    before.write_text(json.dumps({"openapi": "3.0.0", "paths": {"/v1": {"get": {}}}}), encoding="utf-8")
    after.write_text(json.dumps({"openapi": "3.0.0", "paths": {"/v2": {"get": {}}}}), encoding="utf-8")
    _invoke(["api-diff", workspace, str(before), str(after), *root_arg])
    _invoke(["confidence", workspace, value, *root_arg])
    _invoke(["clusters", workspace, *root_arg])
    _invoke(["acquisitions", workspace, *root_arg])

    report = tmp_path / "report.md"
    _invoke(["report", workspace, str(report), *root_arg])
    assert report.is_file()
    _invoke(["demo", "--workspace", "demo-smoke", *root_arg])

    web_calls: list[tuple[str, int]] = []

    def fake_uvicorn_run(_app: object, *, host: str, port: int) -> None:
        web_calls.append((host, port))

    monkeypatch.setattr("uvicorn.run", fake_uvicorn_run)
    _invoke(["web", workspace, "--port", "18767", *root_arg])
    assert web_calls == [("127.0.0.1", 18767)]

    evidence_file = tmp_path / "evidence.txt"
    evidence_file.write_text("deterministic local evidence", encoding="utf-8")
    _invoke(["evidence", workspace, str(evidence_file), *root_arg])
    _invoke(["ai"])
    _invoke(["plugins", "--path", str(tmp_path / "plugins")])
    _invoke(["scope", "https://example.test/", "--allow", "example.test"])
    _invoke(["query", workspace, "legacy", *root_arg])
    _invoke(["notebook", workspace, "--type", "note", "--title", "smoke", "--body", "offline", *root_arg])
    _invoke(["notebook", workspace, "--list-queries", *root_arg])
    _invoke(["evidence-lineage", workspace, "observation:obs-1", *root_arg])
    _invoke(["jobs", workspace, *root_arg])

    monkeypatch.setattr(cli_update, "_is_windows", lambda: False)
    monkeypatch.setattr(
        cli_update,
        "perform_product_update",
        lambda **_kwargs: UpdateCheck(
            current_version="0.5.13",
            available_version="0.5.13",
            update_available=False,
            product="fossilscope",
            artifact="fixture",
            same_version=True,
            forced=False,
            installed=False,
            channel="test",
        ),
    )
    _invoke(["update", "--check"])

    monkeypatch.setattr(
        PassiveHTTPSCollectorRuntime,
        "collect",
        lambda self, url, adapter, *, ack_terms: SimpleNamespace(
            observations=[],
            url=url,
            cache_hit=False,
            sha256="0" * 64,
            size_bytes=0,
            provenance={"adapter": adapter, "terms_acknowledged": ack_terms},
        ),
    )
    _invoke(
        [
            "collect-url",
            workspace,
            "https://example.test/security.txt",
            "securitytxt",
            "--allow",
            "example.test",
            "--ack-terms",
            *root_arg,
        ]
    )
    _invoke(["time-travel", workspace, "--at", "2026-08-10T00:00:00+00:00", *root_arg])
    _invoke(["resurrections", workspace, "--min-gap-days", "1", *root_arg])
    _invoke(["confidence-v2", workspace, value, *root_arg])

    old_mobile = tmp_path / "old-mobile.txt"
    new_mobile = tmp_path / "new-mobile.txt"
    old_mobile.write_text("https://mobile.example.test/auth/v1", encoding="utf-8")
    new_mobile.write_text("https://mobile.example.test/auth/v2", encoding="utf-8")
    _invoke(["mobile-archaeology", workspace, str(old_mobile), str(new_mobile), *root_arg])

    lifecycle = tmp_path / "lifecycle.json"
    lifecycle.write_text(
        json.dumps(
            [
                {
                    "evidence_id": "E-LIFE",
                    "asset_id": "asset-1",
                    "kind": "HISTORICAL_REFERENCE",
                    "source_id": "archive",
                }
            ]
        ),
        encoding="utf-8",
    )
    _invoke(["lifecycle-assess", str(lifecycle)])

    reobserve = tmp_path / "reobserve.json"
    request = {
        "request_id": "REQ-1",
        "asset_id": "asset-1",
        "target": "https://example.test/",
        "reason": "CURRENT_STATE_UNKNOWN",
        "mode": "PASSIVE",
    }
    reobserve.write_text(json.dumps([request]), encoding="utf-8")
    _invoke(["reobserve-plan", str(reobserve)])
    retry = tmp_path / "retry.json"
    retry.write_text(json.dumps(request), encoding="utf-8")
    _invoke(["reobserve-retry", str(retry), "--base-delay", "1", "--max-delay", "2"])

    evolution = tmp_path / "evolution.json"
    evolution.write_text(
        json.dumps(
            [
                {
                    "observation_id": "EV-1",
                    "artifact_id": "api-1",
                    "artifact_kind": "API_SPEC",
                    "version_label": "1",
                    "observed_at": "2025-01-01T00:00:00+00:00",
                    "content_sha256": "0" * 64,
                    "endpoints": ["/v1"],
                    "references": ["https://legacy.example.test/v1"],
                    "source_id": "archive",
                    "evidence_ids": ["E-EV1"],
                    "historical": True,
                },
                {
                    "observation_id": "EV-2",
                    "artifact_id": "api-1",
                    "artifact_kind": "API_SPEC",
                    "version_label": "2",
                    "observed_at": "2026-01-01T00:00:00+00:00",
                    "content_sha256": "1" * 64,
                    "endpoints": ["/v2"],
                    "references": [],
                    "source_id": "repo",
                    "evidence_ids": ["E-EV2"],
                    "historical": False,
                },
            ]
        ),
        encoding="utf-8",
    )
    _invoke(["evolution-diff", str(evolution)])
    _invoke(["stale-references", str(evolution)])

    planning = tmp_path / "planning.json"
    planning.write_text(
        json.dumps(
            [
                {
                    "asset_id": "asset-1",
                    "target": "https://example.test/",
                    "exposure_state": "REACHABILITY_UNKNOWN",
                    "evidence_ids": ["E-PLAN"],
                    "age_days": 400,
                    "current_reference": True,
                }
            ]
        ),
        encoding="utf-8",
    )
    _invoke(["reobservation-priority", str(planning), "--max-requests", "5"])
