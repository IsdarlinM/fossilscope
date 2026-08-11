"""Bounded compatibility bridge for the SRIC 0.5.14 Web catalog.

FossilScope 0.5.14 can install a newer product archive with ``--no-deps`` before the
shared runtime is upgraded. SRIC 0.5.15 contains the canonical fix. This bridge only
intercepts the 0.5.14 TypeError failure class so the Security Workspace can still load
and the shared runtime can subsequently be repaired.
"""

from __future__ import annotations

import importlib.metadata
from typing import Any


def install() -> None:
    try:
        version = importlib.metadata.version("sric-core")
    except importlib.metadata.PackageNotFoundError:
        return
    if version != "0.5.14":
        return

    from sric import web_catalog, web_console

    original = web_catalog._option_metadata
    if getattr(original, "_fossilscope_compat", False):
        return

    def compatible_metadata(param: Any) -> dict[str, Any]:
        try:
            return original(param)
        except TypeError:
            # SRIC's legacy serializer already knows how to distinguish option-like
            # objects via ``opts``. Enrich its result with the keys expected by the
            # guided Workbench rather than dropping the complete catalog.
            payload = web_console._option_metadata(param)
            payload.setdefault("choices", [])
            payload.setdefault("min", None)
            payload.setdefault("max", None)
            payload.setdefault("clamp", False)
            payload.setdefault("path", None)
            payload["parameter_class"] = type(param).__name__
            return payload

    compatible_metadata._fossilscope_compat = True  # type: ignore[attr-defined]
    web_catalog._option_metadata = compatible_metadata
