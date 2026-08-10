from __future__ import annotations

from pathlib import Path
from typing import Any

import click
from fastapi.testclient import TestClient
from typer.main import get_command
from typer.testing import CliRunner

from fossilscope.api_all import create_app
from fossilscope.cli_all import app
from sric.web_catalog import build_json_safe_command_catalog, install_json_safe_catalog
from sric.web_guardrails import SUPPORTED_WEB_CONTROLS
from sric.web_workbench import build_feature_catalog, feature_contract

runner = CliRunner()


def _command_map() -> dict[str, click.Command]:
    root = get_command(app)
    output: dict[str, click.Command] = {}

    def walk(command: click.Command, prefix: tuple[str, ...]) -> None:
        children = getattr(command, "commands", None)
        if not isinstance(children, dict):
            return
        for name, child in children.items():
            if getattr(child, "hidden", False):
                continue
            path = (*prefix, str(name))
            output[" ".join(path)] = child
            walk(child, path)

    walk(root, ())
    return output


def _fixture_value(meta: dict[str, Any], tmp_path: Path, index: int) -> str:
    choices = list(meta.get("choices") or [])
    if choices:
        return str(choices[0])

    path_meta = meta.get("path")
    if isinstance(path_meta, dict):
        if path_meta.get("dir_okay") and not path_meta.get("file_okay"):
            directory = tmp_path / f"param-dir-{index}"
            directory.mkdir(exist_ok=True)
            return str(directory)
        file_path = tmp_path / f"param-file-{index}.txt"
        file_path.write_text("fixture\n", encoding="utf-8")
        return str(file_path)

    type_name = str(meta.get("type") or "").lower()
    minimum = meta.get("min")
    maximum = meta.get("max")
    if "int" in type_name or "range" in type_name:
        candidate = int(minimum) if isinstance(minimum, (int, float)) else 1
        if isinstance(maximum, (int, float)) and candidate > int(maximum):
            candidate = int(maximum)
        return str(candidate)
    if "float" in type_name or "number" in type_name:
        candidate = float(minimum) if isinstance(minimum, (int, float)) else 1.0
        if isinstance(maximum, (int, float)) and candidate > float(maximum):
            candidate = float(maximum)
        return str(candidate)
    if "datetime" in type_name or "date" == type_name:
        return "2026-08-10T12:34:56"
    if "bool" in type_name:
        return "true"
    return f"fixture-{index}"


def _values(meta: dict[str, Any], tmp_path: Path, index: int) -> list[str]:
    count = int(meta.get("nargs", 1))
    if count < 0:
        count = 1
    count = max(1, count)
    return [_fixture_value(meta, tmp_path, index) for _ in range(count)]


def _valid_parse_argv(params: list[dict[str, Any]], tmp_path: Path) -> list[str]:
    options: list[str] = []
    arguments: list[str] = []
    for index, meta in enumerate(params):
        if meta.get("kind") == "argument":
            arguments.extend(_values(meta, tmp_path, index))
            continue
        option = str(meta.get("opts", [""])[0] if meta.get("opts") else "")
        assert option.startswith("-"), meta
        options.append(option)
        if not meta.get("is_flag") and not meta.get("count"):
            options.extend(_values(meta, tmp_path, index))
    return [*options, *arguments]


def test_every_public_command_and_parameter_parses_and_maps_to_web(tmp_path: Path) -> None:
    install_json_safe_catalog()
    cli = build_json_safe_command_catalog("fossilscope.cli_all")
    features = build_feature_catalog("fossilscope.cli_all")
    contract = feature_contract("fossilscope.cli_all")
    commands = _command_map()

    assert contract["complete"] is True
    assert len(cli) == 45
    assert len(features) == 45
    assert set(commands) == {item["path"] for item in cli}
    assert {item["path"] for item in features} == set(commands)

    cli_by_path = {item["path"]: item for item in cli}
    web_by_path = {item["path"]: item for item in features}

    for path, command in commands.items():
        cli_params = cli_by_path[path]["params"]
        web_params = web_by_path[path]["params"]
        assert [item["name"] for item in cli_params] == [item["name"] for item in web_params], path
        assert len(command.params) == len(cli_params), path

        for raw, cli_meta, web_meta in zip(command.params, cli_params, web_params):
            assert cli_meta["parameter_class"] == type(raw).__name__, (path, raw.name)
            assert web_meta["control"] in SUPPORTED_WEB_CONTROLS, (path, raw.name)
            assert web_meta["id"], (path, raw.name)
            if str(getattr(raw, "param_type_name", "")).lower() == "argument" or type(raw).__name__.lower().endswith("argument"):
                assert cli_meta["kind"] == "argument", (path, raw.name)
                assert cli_meta["opts"] == [], (path, raw.name)
                assert web_meta["primary_opt"] is None, (path, raw.name)
            elif cli_meta["kind"] == "option":
                assert cli_meta["opts"], (path, raw.name)
                assert str(cli_meta["opts"][0]).startswith("-"), (path, raw.name)
                assert str(web_meta["primary_opt"]).startswith("-"), (path, raw.name)

        command_tmp = tmp_path / path.replace(" ", "-")
        command_tmp.mkdir(parents=True, exist_ok=True)
        argv = _valid_parse_argv(cli_params, command_tmp)
        with command.make_context(path, argv, resilient_parsing=False) as context:
            assert context.params is not None, path


def test_every_command_rejects_unknown_options_without_raw_exception() -> None:
    for path in _command_map():
        result = runner.invoke(app, [*path.split(), "--sentinel-invalid-option"])
        assert result.exit_code != 0, path
        assert "Traceback" not in result.output, path
        assert result.exception is None or isinstance(result.exception, SystemExit), (
            path,
            type(result.exception).__name__,
        )


def test_every_command_with_required_parameters_fails_missing_input_cleanly() -> None:
    cli = build_json_safe_command_catalog("fossilscope.cli_all")
    for item in cli:
        if not any(bool(param.get("required")) for param in item["params"]):
            continue
        path = str(item["path"])
        result = runner.invoke(app, path.split())
        assert result.exit_code != 0, path
        assert "Traceback" not in result.output, path
        assert result.exception is None or isinstance(result.exception, SystemExit), (
            path,
            type(result.exception).__name__,
        )


def test_workbench_exposes_complete_operation_library_and_recovery_controls(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    page = client.get("/workbench")
    script = client.get("/workbench/app.js")
    catalog = client.get("/api/v1/workbench/catalog")
    coverage = client.get("/api/v1/workbench/coverage")

    assert page.status_code == 200
    assert script.status_code == 200
    assert catalog.status_code == 200
    assert coverage.status_code == 200
    payload = catalog.json()
    assert len(payload["features"]) == 45
    assert payload["contract"]["complete"] is True
    assert coverage.json()["complete"] is True

    for label in ("Run operation", "Cancel", "Refresh"):
        assert label in page.text
    assert "Reload interface" in script.text
    assert "window.location.reload()" in script.text
    assert "unhandledrejection" in script.text
    assert 'button.className = "feature"' in script.text

    for feature in payload["features"]:
        assert feature["title"]
        assert feature["category"]
        for param in feature["params"]:
            assert param["control"] in SUPPORTED_WEB_CONTROLS
