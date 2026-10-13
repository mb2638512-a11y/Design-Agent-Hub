"""Quality specialist for review gates and acceptance criteria."""

from __future__ import annotations

from typing import ClassVar


class QualitySpecialistAgent:
    id = "quality"
    name = "Quality Agent"
    description = "Produces QA criteria for design, software, content, accessibility, and release readiness."
    capabilities: ClassVar[list[str]] = [
        "quality", "qa", "test", "testing", "review", "audit", "accessibility", "wcag",
        "bug", "validate", "validation", "check", "checklist", "security", "release",
        "proofread", "verify output",
    ]

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        return sum(2 for item in self.capabilities if item in normalized)

    async def run(self, task: str) -> dict[str, object]:
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "result_type": "qa_checklist",
            "execution_status": "review_plan_only",
            "task_under_review": task,
            "checks": [
                {"area": "Requirements", "checks": ["Every acceptance criterion is addressed", "Assumptions and gaps are listed"]},
                {"area": "Correctness", "checks": ["Expected behavior is tested", "Invalid inputs and failures are handled"]},
                {"area": "Accessibility", "checks": ["Keyboard and readable-label checks where applicable", "Contrast and text legibility checked for visual assets"]},
                {"area": "Security and privacy", "checks": ["No secrets in code, logs, or deliverables", "External writes require explicit authorization"]},
                {"area": "Delivery", "checks": ["Output opens in its target tool", "File names, formats, and handoff notes are clear"]},
            ],
            "limitations": ["This agent creates a review checklist; it does not claim tests or external checks were actually run."],
        }
