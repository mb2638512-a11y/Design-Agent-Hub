"""Delivery specialist for packaging and handoff planning."""

from __future__ import annotations

from typing import ClassVar


class DeliverySpecialistAgent:
    id = "delivery"
    name = "Delivery Agent"
    description = "Prepares handoff manifests, export checks, client-ready notes, and delivery acceptance steps."
    capabilities: ClassVar[list[str]] = [
        "deliver", "delivery", "handoff", "export", "package", "packaging", "client-ready",
        "client ready", "publish", "launch", "final files", "manifest", "handover", "submit",
    ]

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        return sum(2 for item in self.capabilities if item in normalized)

    async def run(self, task: str) -> dict[str, object]:
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "result_type": "delivery_manifest",
            "execution_status": "handoff_plan_only",
            "task": task,
            "manifest": [
                {"item": "Editable source", "status": "confirm availability and access"},
                {"item": "Final exports", "status": "confirm requested format, dimensions, and quality"},
                {"item": "Preview", "status": "include a review image or screenshot where applicable"},
                {"item": "Usage rights", "status": "confirm licenses, attribution, and client-provided asset permissions"},
                {"item": "Handoff notes", "status": "include filenames, edit instructions, and known limitations"},
                {"item": "Approval", "status": "obtain client approval before publishing or overwriting"},
            ],
            "limitations": ["This agent prepares a manifest; it does not upload, email, publish, or export files itself."],
        }
