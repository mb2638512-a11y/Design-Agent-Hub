"""Minimal Canva Connect API adapter; user OAuth credentials and scopes are required."""

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
        return ConnectorStatus(
            provider="canva",
            configured=bool(self.token),
            capabilities=["list_designs"] if self.token else [],
            note="Requires a valid OAuth access token with appropriate scopes; token presence is not validation.",
        )

    async def list_designs(self, limit: int = 20) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("Canva is not configured. Complete the official OAuth flow and set CANVA_ACCESS_TOKEN privately.")
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/v1/designs",
                params={"limit": limit},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
            return response.json()
