"""Design specialist with planning and a deterministic editable SVG starter."""

from __future__ import annotations

from html import escape
from typing import ClassVar

from ..catalog import search_catalog
from ..planner import PlanRequest, create_plan


class DesignSpecialistAgent:
    id = "design"
    name = "Design Agent"
    description = "Plans design work and can draft a simple editable SVG starter for common static graphics."
    capabilities: ClassVar[list[str]] = [
        "ui ux", "website", "landing page", "mobile app", "dashboard", "wireframe",
        "prototype", "design system", "branding", "logo", "social media", "instagram",
        "youtube thumbnail", "advertising", "presentation", "pitch deck", "document",
        "infographic", "poster", "flyer", "ecommerce", "product image", "photo editing",
        "video graphics", "animation", "svg", "vector", "illustration", "3d", "product render",
        "accessibility", "figma", "canva", "penpot", "design",
    ]
    _svg_keywords: ClassVar[tuple[str, ...]] = (
        "instagram post", "social post", "poster", "thumbnail", "banner", "graphic", "svg",
    )

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        score = sum(2 for capability in self.capabilities if capability in normalized)
        if search_catalog(task):
            score += 2
        return score

    @staticmethod
    def _make_svg(task: str) -> str:
        headline = escape(task.strip().replace("\n", " ")[:58] or "Your next big idea")
        subtitle = "A starter design — edit the copy, colors, and brand assets."
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080" role="img" aria-labelledby="title desc">
  <title id="title">{headline}</title>
  <desc id="desc">Editable social graphic starter with a bold headline and simple visual hierarchy.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#312e81"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22d3ee"/>
      <stop offset="100%" stop-color="#a78bfa"/>
    </linearGradient>
  </defs>
  <rect width="1080" height="1080" rx="48" fill="url(#bg)"/>
  <circle cx="900" cy="190" r="210" fill="#818cf8" opacity=".15"/>
  <circle cx="160" cy="900" r="250" fill="#22d3ee" opacity=".10"/>
  <rect x="88" y="100" width="110" height="10" rx="5" fill="url(#accent)"/>
  <text x="88" y="180" fill="#cbd5e1" font-family="Inter, Arial, sans-serif" font-size="24" letter-spacing="5">DESIGN AGENT HUB</text>
  <text x="88" y="390" fill="#ffffff" font-family="Inter, Arial, sans-serif" font-size="64" font-weight="700">{headline}</text>
  <foreignObject x="88" y="440" width="820" height="150">
    <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Inter,Arial,sans-serif;color:#cbd5e1;font-size:28px;line-height:1.4">{escape(subtitle)}</div>
  </foreignObject>
  <rect x="88" y="680" width="280" height="72" rx="36" fill="url(#accent)"/>
  <text x="228" y="726" text-anchor="middle" fill="#0f172a" font-family="Inter, Arial, sans-serif" font-size="24" font-weight="700">GET STARTED</text>
  <text x="88" y="980" fill="#94a3b8" font-family="Inter, Arial, sans-serif" font-size="18">Replace this copy and add your approved brand assets.</text>
</svg>'''

    async def run(self, task: str) -> dict[str, object]:
        plan = await create_plan(PlanRequest(request=task))
        result: dict[str, object] = {
            "agent_id": self.id,
            "agent_name": self.name,
            "execution_status": plan.execution_status,
            "result_type": "design_plan",
            "result": plan.model_dump(),
        }
        if any(keyword in task.casefold() for keyword in self._svg_keywords):
            result["starter_asset"] = {
                "format": "svg",
                "editable": True,
                "execution_status": "generated_in_response",
                "width": 1080,
                "height": 1080,
                "content": self._make_svg(task),
                "note": "A deterministic starter graphic, not a polished client-approved design. Review text, accessibility, and brand rights before use.",
            }
        return result
