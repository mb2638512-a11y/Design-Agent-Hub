"""Design specialist agent wrapping the existing catalog and workflow planner."""

from __future__ import annotations

from ..catalog import search_catalog
from ..planner import PlanRequest, create_plan


class DesignSpecialistAgent:
    id = "design"
    name = "Design Agent"
    description = "Plans UI/UX, brand, social, graphics, documents, motion, vector, and 3D design work."
    capabilities = [
        "ui ux", "website", "landing page", "mobile app", "dashboard", "wireframe",
        "prototype", "design system", "branding", "logo", "social media", "instagram",
        "youtube thumbnail", "advertising", "presentation", "pitch deck", "document",
        "infographic", "poster", "flyer", "ecommerce", "product image", "photo editing",
        "video graphics", "animation", "svg", "vector", "illustration", "3d", "product render",
        "accessibility", "figma", "canva", "penpot", "design",
    ]

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        score = sum(2 for capability in self.capabilities if capability in normalized)
        if search_catalog(task):
            score += 2
        return score

    async def run(self, task: str) -> dict[str, object]:
        plan = await create_plan(PlanRequest(request=task))
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "execution_status": plan.execution_status,
            "result_type": "design_plan",
            "result": plan.model_dump(),
        }
