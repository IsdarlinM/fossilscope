from __future__ import annotations

"""Bounded compatibility bridge for SRIC 0.5.14/0.5.15 Web catalogs.

SRIC 0.5.14 can raise on modern ``TyperArgument`` objects. SRIC 0.5.15 no longer
raises, but Typer 0.26 arguments also expose ``opts`` and can therefore be mistaken for
options by the legacy structural fallback. SRIC 0.5.16 contains the canonical fix.
This bridge keeps product-first repair/update paths usable until the shared runtime is
advanced to the signed 0.5.16 snapshot.
"""

import importlib.metadata
from typing import Any


def install() -> None:
    try:
        version = importlib.metadata.version("sric-core")
    except importlib.metadata.PackageNotFoundError:
        return
    if version not in {"0.5.14", "0.5.15"}:
        return

    from sric import web_catalog, web_console

    original = web_catalog._option_metadata
    if getattr(original, "_fossilscope_compat", False):
        return

    def compatible_metadata(param: Any) -> dict[str, Any]:
        try:
            payload = original(param)
        except TypeError:
            payload = web_console._option_metadata(param)

        payload.setdefault("choices", [])
        payload.setdefault("min", None)
        payload.setdefault("max", None)
        payload.setdefault("clamp", False)
        payload.setdefault("path", None)
        payload["parameter_class"] = type(param).__name__

        kind_hint = str(getattr(param, "param_type_name", "") or "").lower()
        class_name = type(param).__name__.lower()
        is_argument = kind_hint == "argument" or class_name.endswith("argument")
        if is_argument:
            payload.update(
                {
                    "kind": "argument",
                    "opts": [],
                    "secondary_opts": [],
                    "help": str(getattr(param, "help", "") or ""),
                    "is_flag": False,
                    "count": False,
                }
            )
        return payload

    compatible_metadata._fossilscope_compat = True  # type: ignore[attr-defined]
    web_catalog._option_metadata = compatible_metadata
