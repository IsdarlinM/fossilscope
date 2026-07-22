from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Observation

MAX_BYTES = 10 * 1024 * 1024
SUPPORTED_ADAPTERS = {
    "ct",
    "dns",
    "repo",
    "package",
    "openapi",
    "js",
    "sourcemap",
    "docs",
    "archive",
    "securitytxt",
    "sitemap",
}


def _read(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError("collector input must be a regular non-symlink file")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"collector input exceeds {MAX_BYTES} byte limit")
    return path.read_text(encoding="utf-8", errors="replace")


def _id(adapter: str, value: str, suffix: str = "") -> str:
    digest = hashlib.sha256(f"{adapter}:{value}:{suffix}".encode()).hexdigest()[:14].upper()
    return f"COL-{digest}"


def _iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _text_refs(text: str) -> list[tuple[str, str]]:
    urls = {
        value.rstrip(".,;)'\"")
        for value in re.findall(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+", text)
    }
    domains = {
        value.lower()
        for value in re.findall(r"(?<![@\w.-])(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,63}(?![\w.-])", text)
    }
    out = [("endpoint", value) for value in urls]
    out.extend(("domain", value) for value in domains if not any(value in url for url in urls))
    return sorted(set(out))


def collect_passive(path: Path, adapter: str) -> list[Observation]:
    """Normalize an explicit local export/artifact; never performs network collection."""
    adapter = adapter.lower().strip()
    if adapter not in SUPPORTED_ADAPTERS:
        raise ValueError(f"unsupported passive adapter: {adapter}")
    text = _read(path)
    source = f"adapter:{adapter}"
    out: list[Observation] = []

    if adapter == "openapi":
        payload = json.loads(text)
        paths = payload.get("paths", {}) if isinstance(payload, dict) else {}
        if not isinstance(paths, dict):
            raise ValueError("OpenAPI paths must be an object")
        for api_path, operations in sorted(paths.items()):
            methods = sorted(operations) if isinstance(operations, dict) else []
            out.append(
                Observation(
                    observation_id=_id(adapter, str(api_path)),
                    entity_type="api_endpoint",
                    value=str(api_path),
                    source=source,
                    current_reference=True,
                    metadata={"artifact": path.name, "methods": methods, "adapter": adapter},
                )
            )
        return out

    if adapter in {"ct", "dns"}:
        payload = json.loads(text)
        items: list[Any]
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            candidate = payload.get("entries") or payload.get("records") or payload.get("results")
            items = candidate if isinstance(candidate, list) else [payload]
        else:
            raise ValueError("collector JSON must be an object or array")
        values: set[tuple[str, str, str | None, str | None]] = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            if adapter == "ct":
                names = item.get("dns_names") or item.get("name_value") or item.get("common_name") or []
                if isinstance(names, str):
                    names = names.splitlines()
                if not isinstance(names, list):
                    names = []
                for name in names:
                    if isinstance(name, str) and name.strip():
                        values.add(("domain", name.strip().lstrip("*.").lower(), item.get("not_before"), item.get("not_after")))
            else:
                name = item.get("name") or item.get("hostname")
                value = item.get("value") or item.get("address") or item.get("target")
                if isinstance(name, str) and name:
                    values.add(("domain", name.rstrip(".").lower(), None, None))
                if isinstance(value, str) and value:
                    etype = "ip" if re.fullmatch(r"[0-9a-fA-F:.]+", value) else "domain"
                    values.add((etype, value.rstrip(".").lower(), None, None))
        for etype, value, first, last in sorted(values):
            out.append(
                Observation(
                    observation_id=_id(adapter, value),
                    entity_type=etype,
                    value=value,
                    source=source,
                    first_seen=_iso(first),
                    last_seen=_iso(last),
                    metadata={"artifact": path.name, "adapter": adapter},
                )
            )
        return out

    # Repositories, package metadata, JS/source maps, docs, archives, security.txt and sitemaps
    # are treated strictly as user-supplied untrusted text. Only deterministic references are extracted.
    for etype, value in _text_refs(text):
        out.append(
            Observation(
                observation_id=_id(adapter, value),
                entity_type=etype,
                value=value,
                source=source,
                current_reference=adapter in {"repo", "package", "js", "sourcemap", "securitytxt", "sitemap"},
                metadata={"artifact": path.name, "adapter": adapter, "extraction": "deterministic_regex"},
            )
        )
    return out
