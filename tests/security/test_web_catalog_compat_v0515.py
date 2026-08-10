from __future__ import annotations

import importlib.metadata

import pytest
import typer
from typer.main import get_command

from fossilscope import web_catalog_compat
from sric import web_catalog, web_console


class ThirdPartyParameter:
    name = "custom_parameter"
    required = False
    multiple = False
    nargs = 1
    default = None
    type = None


def _real_typer_argument() -> object:
    app = typer.Typer()

    @app.command()
    def sample(target: str = typer.Argument(..., help="Target value")) -> None:
        pass

    root = get_command(app)
    command = root.commands["sample"] if hasattr(root, "commands") else root
    return command.params[0]


def test_sric_0514_unknown_parameter_type_does_not_collapse_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    def strict_legacy_serializer(_param: object) -> dict[str, object]:
        raise TypeError("unsupported CLI parameter type in Web catalog: ThirdPartyParameter")

    monkeypatch.setattr(importlib.metadata, "version", lambda name: "0.5.14" if name == "sric-core" else "0")
    monkeypatch.setattr(web_catalog, "_option_metadata", strict_legacy_serializer)

    web_catalog_compat.install()
    payload = web_catalog._option_metadata(ThirdPartyParameter())

    assert payload["name"] == "custom_parameter"
    assert payload["kind"] == "argument"
    assert payload["choices"] == []
    assert payload["min"] is None
    assert payload["max"] is None
    assert payload["path"] is None
    assert payload["parameter_class"] == "ThirdPartyParameter"
    assert web_console._option_metadata(ThirdPartyParameter())["kind"] == "argument"


def test_legacy_sric_versions_preserve_real_typer_argument_positional_semantics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    param = _real_typer_argument()
    assert type(param).__name__ == "TyperArgument"
    assert getattr(param, "param_type_name", None) == "argument"
    assert list(getattr(param, "opts", []))

    for version in ("0.5.14", "0.5.15"):
        monkeypatch.setattr(
            importlib.metadata,
            "version",
            lambda name, selected=version: selected if name == "sric-core" else "0",
        )
        # Reinstall the bridge from a clean legacy-compatible serializer for each release.
        monkeypatch.setattr(web_catalog, "_option_metadata", web_console._option_metadata)
        web_catalog_compat.install()
        payload = web_catalog._option_metadata(param)
        assert payload["kind"] == "argument", version
        assert payload["opts"] == [], version
        assert payload["secondary_opts"] == [], version
        assert payload["help"] == "Target value", version
        assert payload["is_flag"] is False, version
        assert payload["count"] is False, version
        assert payload["parameter_class"] == "TyperArgument", version


def test_current_sric_does_not_install_product_compat_override(monkeypatch: pytest.MonkeyPatch) -> None:
    marker = object()
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "0.5.16" if name == "sric-core" else "0")
    monkeypatch.setattr(web_catalog, "_option_metadata", marker)
    web_catalog_compat.install()
    assert web_catalog._option_metadata is marker
