"""Small contract for pluggable specialist agents."""

from __future__ import annotations

from typing import Protocol


class SpecialistAgent(Protocol):
    id: str
    name: str
    description: str
    capabilities: list[str]

    def match_score(self, task: str) -> int:
        """Return zero when the agent cannot handle the task; higher is better."""

    async def run(self, task: str) -> dict[str, object]:
        """Handle the task and return a JSON-serializable result."""
