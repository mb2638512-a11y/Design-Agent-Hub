"""Content specialist for marketing copy, scripts, and structured content briefs."""

from __future__ import annotations

from html import escape
from typing import ClassVar


class ContentSpecialistAgent:
    id = "content"
    name = "Content Agent"
    description = "Creates editable starter copy and structured content packs for marketing and creator workflows."
    capabilities: ClassVar[list[str]] = [
        "copywriting", "copy writing", "write caption", "caption", "slogan", "tagline",
        "product description", "blog post", "article", "email copy", "newsletter copy",
        "youtube script", "video script", "shorts script", "reel script", "social copy",
        "content calendar", "ad copy", "marketing copy", "course outline", "lesson plan",
        "landing page copy", "call to action", "cta", "headline", "write a post",
    ]

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        return sum(4 for capability in self.capabilities if capability in normalized)

    @staticmethod
    def _starter_copy(task: str) -> dict[str, str]:
        subject = escape(task.strip()[:180])
        return {
            "headline": subject,
            "supporting_copy": (
                "Make the next step clear. Explain the benefit in plain language, "
                "support it with a specific proof point, and keep the message focused on the audience."
            ),
            "call_to_action": "Learn more",
            "disclosure": "Draft copy only. Verify all claims, prices, offers, and legal statements before publishing.",
        }

    async def run(self, task: str) -> dict[str, object]:
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "result_type": "content_starter_pack",
            "execution_status": "draft_generated",
            "task": task,
            "content": self._starter_copy(task),
            "workflow": [
                "Identify the audience, purpose, platform, and desired action.",
                "Draft a headline, supporting message, and call to action.",
                "Check tone, readability, factual claims, and platform constraints.",
                "Adapt length and formatting to the target channel.",
                "Obtain human approval before publication.",
            ],
            "limitations": [
                "This is a deterministic starter, not a fact-checked or audience-tested campaign.",
                "No content is published or sent by this agent.",
            ],
        }
