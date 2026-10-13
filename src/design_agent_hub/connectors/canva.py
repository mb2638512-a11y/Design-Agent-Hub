"""Canva Connect API adapter; requires official OAuth credentials and endpoint scopes."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .base import ConnectorStatus


class CanvaConnector:
    def __init__(self, token: str | None = None, base_url: str | None = None) -> None:
        self.token = token if token is not None else os.getenv("CANVA_ACCESS_TOKEN", "")
        self.base_url = (base_url or os.getenv("CANVA_API_BASE_URL", "https://api.canva.com/rest")).rstrip("/")

    def status(self) -> ConnectorStatus:
        capabilities = ["list_designs", "create_design", "start_export", "get_export"] if self.token else []
        return ConnectorStatus(
            provider="canva",
            configured=bool(self.token),
            capabilities=capabilities,
            note="Requires a valid OAuth token and endpoint-specific scopes; token presence is not validation.",
        )

    def _headers(self) -> dict[str, str]:
        if not self.token:
            raise RuntimeError("Canva is not configured. Complete official OAuth and set CANVA_ACCESS_TOKEN privately.")
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def list_designs(self, limit: int = 20) -> dict[str, Any]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/v1/designs", params={"limit": limit}, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def create_design(self, title: str, width: int, height: int) -> dict[str, Any]:
        """Create a blank custom design; actual creation requires explicit user approval."""
        title = title.strip()
        if not title or len(title) > 200:
            raise ValueError("title must contain 1-200 characters")
        if not (40 <= width <= 8000 and 40 <= height <= 8000 and width * height <= 25_000_000):
            raise ValueError("dimensions must be 40-8000 pixels and total area must not exceed 25,000,000 pixels")
        payload = {"title": title, "design_type": {"type": "custom", "width": width, "height": height}}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}/v1/designs", headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    async def start_export(self, design_id: str, file_format: str = "png") -> dict[str, Any]:
        """Start a Canva export job; may use provider quota and requires explicit user approval."""
        supported = {"pdf", "jpg", "png", "gif", "pptx", "mp4", "csv", "html_bundle", "html_standalone"}
        if file_format not in supported:
            raise ValueError(f"Unsupported format. Choose one of: {
.join(sorted(supported))}")
        if not design_id.strip():
            raise ValueError("design_id is required")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/exports",
                headers=self._headers(),
                json={"design_id": design_id, "format": {"type": file_format}},
            )
            response.raise_for_status()
            return response.json()

    async def get_export(self, export_id: str) -> dict[str, Any]:
        """Read the status/result of an existing export job."""
        if not export_id.strip():
            raise ValueError("export_id is required")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}/v1/exports/{export_id}", headers=self._headers())
            response.raise_for_status()
            return response.json()
