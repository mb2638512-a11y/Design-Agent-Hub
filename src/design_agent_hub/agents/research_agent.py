"""Research specialist for structured, source-aware research plans."""

from __future__ import annotations

from typing import ClassVar


class ResearchSpecialistAgent:
    id = "research"
    name = "Research Agent"
    description = "Structures research questions, evidence requirements, comparisons, and source verification."
    capabilities: ClassVar[list[str]] = [
        "research", "compare", "comparison", "competitor", "market", "sources", "evidence",
        "verify", "fact check", "fact-check", "investigate", "benchmark", "pricing", "latest",
        "review options", "find information",
    ]

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        return sum(2 for item in self.capabilities if item in normalized)

    async def run(self, task: str) -> dict[str, object]:
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "result_type": "research_brief",
            "execution_status": "research_plan_only",
            "research_question": task,
            "workflow": [
                "Turn the request into answerable questions and define the decision to support.",
                "Prefer primary sources, official documentation, and dated evidence.",
                "Record source URL, publication/update date, key claim, and confidence for each finding.",
                "Cross-check important claims against an independent source.",
                "Separate verified facts, estimates, assumptions, and unresolved questions.",
                "Summarize findings with trade-offs and a recommendation tied to the evidence.",
            ],
            "limitations": [
                "This specialist does not perform live web searches in its current implementation.",
                "Current prices, availability, and recent claims must be verified against live sources before use.",
            ],
        }
