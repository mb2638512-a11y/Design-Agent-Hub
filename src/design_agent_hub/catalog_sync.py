"""Explicit, read-only sync for allowlisted upstream tool metadata catalogs.

This module never installs, imports, or executes discovered projects. Network access
is limited to hard-coded HTTPS feeds, with bounded timeouts and response sizes.
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from .tool_registry import list_catalog_sources

MAX_RESPONSE_BYTES = 5 * 1024 * 1024
TIMEOUT_SECONDS = 8.0


def _normalise_source(source_id: str, payload: Any) -> list[dict[str, Any]]:
    """Convert upstream payloads to a conservative metadata-only record list."""
    records: list[dict[str, Any]] = []
    if isinstance(payload, list):
        candidates = payload
    elif isinstance(payload, dict):
        # APIs.guru is a mapping of API ids to OpenAPI directory metadata.
        candidates = []
        for key, value in payload.items():
            if isinstance(value, dict):
                info = value.get("info", {}) if isinstance(value.get("info"), dict) else {}
                candidates.append({
                    "id": key,
                    "name": info.get("title") or key,
                    "description": info.get("description", ""),
                    "version": info.get("version", ""),
                    "kind": "api",
                })
    else:
        return records

    for index, item in enumerate(candidates[:5000]):
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("title") or item.get("id")
        if not isinstance(name, str) or not name.strip():
            continue
        # Deliberately keep only display-safe metadata fields. Never surface commands
        # or configuration from an untrusted feed as executable instructions.
        records.append({
            "id": str(item.get("id") or f"{source_id}-{index}")[:200],
            "name": name.strip()[:300],
            "description": str(item.get("description") or item.get("purpose") or "")[:1000],
            "kind": "mcp" if source_id == "mcphq-landscape" else "api",
            "source_id": source_id,
            "source_verified": False,
            "execution_status": "metadata_only_unverified",
        })
    return records


async def sync_catalog_source(source_id: str) -> dict[str, Any]:
    """Fetch one allowlisted catalog on explicit request; return metadata only."""
    source = next((s for s in list_catalog_sources() if s["id"] == source_id), None)
    if source is None:
        raise ValueError("Unknown catalog source; choose a source returned by list_catalog_sources().")

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(TIMEOUT_SECONDS),
            follow_redirects=False,
            headers={"Accept": "application/json", "User-Agent": "Design-Agent-Hub-catalog-sync/1.0"},
        ) as client:
            async with client.stream("GET", source["url"]) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if "json" not in content_type:
                    raise ValueError("Upstream catalog did not return a JSON content type.")
                chunks = bytearray()
                async for chunk in response.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > MAX_RESPONSE_BYTES:
                        raise ValueError("Upstream catalog exceeded the 5 MiB response limit.")
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Catalog fetch failed: {type(exc).__name__}") from exc

    try:
        payload = json.loads(chunks)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("Upstream catalog returned invalid JSON.") from exc

    records = _normalise_source(source_id, payload)
    return {
        "source": source_id,
        "source_url": source["url"],
        "count": len(records),
        "records": records,
        "execution_status": "metadata_only_unverified",
        "installed_anything": False,
        "executed_external_code": False,
        "truncated": len(records) >= 5000,
    }
