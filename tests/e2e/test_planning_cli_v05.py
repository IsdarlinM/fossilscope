import json
from pathlib import Path

from typer.testing import CliRunner

from fossilscope.cli_all import app

runner = CliRunner()


def test_reobservation_priority_cli(tmp_path: Path) -> None:
    path = tmp_path / "candidates.json"
    path.write_text(
        json.dumps(
            [
                {
                    "asset_id": "legacy-api",
                    "target": "https://legacy.example.test/api",
                    "exposure_state": "REACHABILITY_UNKNOWN",
                    "current_reference": True,
                }
            ]
        ),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["reobservation-priority", str(path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["planned_request_count"] == 1
    assert payload["requests"][0]["mode"] == "PASSIVE"
    assert payload["requests_sent"] == 0
