from __future__ import annotations

import importlib.metadata

from fossilscope import web_catalog_compat
from sric import web_catalog, web_console


class ThirdPartyParameter:
    name = "custom_parameter"
    required = False
    multiple = False
    nargs = 1
    default = None
    type = None


def test_sric_0514_unknown_parameter_type_does_not_collapse_catalog(monkeypatch) -> None:
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
