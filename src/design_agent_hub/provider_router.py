"""Deterministic tool routing with a free-first policy.

This module recommends providers; it does not claim account entitlements or execute
third-party actions. Live usage and plan availability must be checked by the client.
"""
from __future__ import annotations

from typing import Any

PROVIDERS: list[dict[str, Any]] = [
    {
        "id": "penpot",
        "name": "Penpot",
        "best_for": ["ui_ux", "website_app", "wireframe", "prototype", "design_system", "design_to_code"],
        "free_status": "free_core_open_source",
        "integration": "Official Penpot MCP server; user must connect a Penpot file/session",
        "limits": "Hosted account/storage and feature availability may change; MCP needs setup and a connected file.",
        "priority": 10,
    },
    {
        "id": "canva",
        "name": "Canva",
        "best_for": ["social_media", "thumbnail", "presentation", "marketing", "poster", "flyer", "brand_assets"],
        "free_status": "free_tier_with_feature_limits",
        "integration": "Official Canva MCP/Connect API; account authorization and scopes required",
        "limits": "Resize, Autofill, Brand Templates, and some API actions can require paid tiers.",
        "priority": 20,
    },
    {
        "id": "figma",
        "name": "Figma",
        "best_for": ["ui_ux", "website_app", "wireframe", "prototype", "design_system", "handoff"],
        "free_status": "free_starter_with_limits",
        "integration": "Figma MCP or local Design Agent Hub plugin; authorized account required",
        "limits": "Starter drafts/team collaboration and MCP tool calls have plan/seat limits.",
        "priority": 30,
    },
    {
        "id": "inkscape",
        "name": "Inkscape",
        "best_for": ["vector_graphic", "logo", "illustration", "print_design", "svg_icon"],
        "free_status": "free_open_source_desktop",
        "integration": "Generate SVG assets or open/edit them in Inkscape; no direct connector is configured",
        "limits": "Agent cannot control the desktop app unless a separate local automation is installed.",
        "priority": 35,
    },
    {
        "id": "gimp",
        "name": "GIMP",
        "best_for": ["photo_editing", "raster_graphic", "background_removal", "image_retouch"],
        "free_status": "free_open_source_desktop",
        "integration": "Use exported raster assets; no direct connector is configured",
        "limits": "Desktop editing requires manual work or separately configured automation.",
        "priority": 36,
    },
    {
        "id": "krita",
        "name": "Krita",
        "best_for": ["digital_painting", "illustration", "concept_art"],
        "free_status": "free_open_source_desktop",
        "integration": "Use generated/imported assets; no direct connector is configured",
        "limits": "Desktop editing requires manual work or separately configured automation.",
        "priority": 37,
    },
    {
        "id": "blender",
        "name": "Blender",
        "best_for": ["3d", "motion_video", "product_render", "3d_mockup"],
        "free_status": "free_open_source_desktop",
        "integration": "Can use generated scripts/assets if Blender is installed; no remote connector is configured",
        "limits": "Rendering needs local/cloud compute and installed Blender.",
        "priority": 38,
    },
    {
        "id": "libreoffice",
        "name": "LibreOffice Draw/Impress",
        "best_for": ["presentation", "documents", "print_design", "diagram", "infographic"],
        "free_status": "free_open_source_desktop",
        "integration": "Can create compatible ODP/ODG/PDF files; no direct connector is configured",
        "limits": "Advanced editable layouts may need manual refinement.",
        "priority": 39,
    },
    {
        "id": "excalidraw",
        "name": "Excalidraw",
        "best_for": ["diagram", "flowchart", "wireframe", "whiteboard"],
        "free_status": "free_web_tool_open_source",
        "integration": "Export/import Excalidraw JSON or SVG; no direct connector is configured",
        "limits": "Collaboration and hosted capabilities depend on the selected service.",
        "priority": 40,
    },
    {
        "id": "html_svg",
        "name": "HTML/CSS/SVG tools",
        "best_for": ["website_app", "vector_graphic", "banner", "diagram", "simple_graphic", "export"],
        "free_status": "free_open_standards",
        "integration": "Generate local source files; preview/export in a browser or open-source editor",
        "limits": "Complex editable documents may need manual refinement or another design application.",
        "priority": 40,
    },
]

KEYWORDS: dict[str, list[str]] = {
    "social_media": ["social", "instagram", "facebook post", "linkedin post", "pinterest", "tiktok cover"],
    "thumbnail": ["thumbnail", "youtube cover", "channel banner"],
    "presentation": ["presentation", "pitch deck", "slides", "webinar deck"],
    "marketing": ["advert", "ad creative", "campaign", "marketing", "promotion"],
    "poster": ["poster", "flyer", "brochure", "invitation", "menu"],
    "brand_assets": ["logo", "brand", "identity", "brand kit"],
    "ui_ux": ["ui", "ux", "dashboard", "wireframe", "prototype", "design system", "app screen"],
    "website_app": ["website", "web app", "mobile app", "landing page", "dashboard", "responsive"],
    "wireframe": ["wireframe", "low fidelity"],
    "prototype": ["prototype", "interactive flow"],
    "design_system": ["design system", "components", "tokens"],
    "design_to_code": ["design to code", "code from design", "inspect design"],
    "handoff": ["handoff", "developer handoff", "inspect panel"],
    "vector_graphic": ["svg", "vector", "icon"],
    "diagram": ["diagram", "flowchart", "process map"],
    "simple_graphic": ["graphic", "illustration", "visual"],
    "export": ["export", "png", "jpg", "pdf"],
    "photo_editing": ["photo edit", "retouch", "background removal", "remove background", "color correction", "product photo"],
    "raster_graphic": ["raster", "image retouch", "pixel edit"],
    "background_removal": ["background removal", "remove background", "transparent background"],
    "image_retouch": ["retouch", "photo cleanup", "clean up photo"],
    "digital_painting": ["digital painting", "paint", "concept art"],
    "illustration": ["illustration", "vector illustration", "mascot", "sticker"],
    "concept_art": ["concept art", "character concept"],
    "logo": ["logo", "vector logo"],
    "print_design": ["print design", "business card", "print-ready"],
    "svg_icon": ["svg icon", "icon set", "vector icon"],
    "3d": ["3d", "three-dimensional"],
    "product_render": ["product render", "3d product", "product visualization"],
    "3d_mockup": ["3d mockup", "mockup scene"],
    "motion_video": ["motion graphic", "animated", "animation", "video overlay", "storyboard", "lower third"],
    "whiteboard": ["whiteboard", "brainstorm"],
}


def recommend_tools(task: str, connected: list[str] | None = None) -> dict[str, Any]:
    """Rank tools for a task, preferring free options and disclosing prerequisites."""
    normalized = task.lower()
    matched = [category for category, words in KEYWORDS.items() if any(word in normalized for word in words)]
    if not matched:
        matched = ["simple_graphic"]
    scored: list[tuple[int, dict[str, Any]]] = []
    for provider in PROVIDERS:
        score = sum(1 for category in matched if category in provider["best_for"])
        if score:
            scored.append((score, provider))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["priority"]))
    connected_set = {item.lower() for item in (connected or [])}
    candidates = []
    for score, provider in scored:
        candidates.append({
            "id": provider["id"],
            "name": provider["name"],
            "match_score": score,
            "free_status": provider["free_status"],
            "connection_status": "connected_by_user" if provider["id"] in connected_set else "not_verified",
            "integration": provider["integration"],
            "limits": provider["limits"],
        })
    return {
        "task": task,
        "matched_categories": matched,
        "policy": "free_first; never purchase, publish, overwrite, or share externally without explicit approval",
        "recommended_tool": candidates[0]["id"] if candidates else "html_svg",
        "candidates": candidates,
        "execution_status": "recommendation_only",
        "next_steps": [
            "Check whether the recommended provider is connected and authorized.",
            "Check current plan, feature entitlement, and rate limits before execution.",
            "If unavailable or paid, try the next eligible free candidate.",
            "Ask the user before any paid action or external publishing.",
            "Inspect the final output and report any manual step or limitation.",
        ],
    }
