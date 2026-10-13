"""Minimal Figma REST adapter. Only call operations with authorized credentials."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import httpx

from .base import ConnectorStatus


class FigmaConnector:
    def __init__(self, token: str | None = None, base_url: str | None = None) -> None:
        self.token = token if token is not None else os.getenv("FIGMA_ACCESS_TOKEN", "")
        self.base_url = (base_url or os.getenv("FIGMA_API_BASE_URL", "https://api.figma.com")).rstrip("/")

    def status(self) -> ConnectorStatus:
        return ConnectorStatus(
            provider="figma",
            configured=bool(self.token),
            capabilities=["get_file", "export_node_images"] if self.token else [],
            note="Token is not validated until a request is made. Use least-privilege credentials.",
        )

    async def get_file(self, file_key: str) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("Figma is not configured. Set FIGMA_ACCESS_TOKEN privately.")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v1/files/{quote(file_key, safe='')}",
                headers={"X-Figma-Token": self.token},
            )
            response.raise_for_status()
            return response.json()

    async def export_node_images(self, file_key: str, node_ids: list[str], image_format: str = "png") -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("Figma is not configured. Set FIGMA_ACCESS_TOKEN privately.")
        if image_format not in {"png", "jpg", "svg", "pdf"}:
            raise ValueError("image_format must be png, jpg, svg, or pdf")
        if not node_ids or len(node_ids) > 100:
            raise ValueError("Provide between 1 and 100 node IDs")
        params = {"ids": ",".join(node_ids), "format": image_format}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v1/images/{quote(file_key, safe='')}",
                params=params,
                headers={"X-Figma-Token": self.token},
            )
            response.raise_for_status()
            return response.json()
