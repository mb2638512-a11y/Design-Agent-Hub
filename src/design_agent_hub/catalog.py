"""Canonical design category catalog used by the planner and integrations."""

from __future__ import annotations

CATALOG: list[dict[str, object]] = [
    {"id": "product_ui_ux", "name": "Product UI/UX", "jobs": ["product discovery brief", "user personas", "user journey map", "information architecture", "user flow", "low-fidelity wireframes", "high-fidelity screen specification", "responsive layout plan", "interactive prototype plan", "usability review", "accessibility review", "design handoff"]},
    {"id": "web_design", "name": "Websites and landing pages", "jobs": ["website sitemap", "landing page", "marketing website", "portfolio website", "SaaS website", "pricing page", "conversion-focused page", "responsive page variants"]},
    {"id": "mobile_design", "name": "Mobile apps", "jobs": ["iOS screen brief", "Android screen brief", "onboarding flow", "settings screens", "mobile navigation", "empty/error/loading states", "app store preview graphics"]},
    {"id": "design_systems", "name": "Design systems", "jobs": ["color tokens", "typography scale", "spacing tokens", "component inventory", "button/input states", "design system documentation", "component QA checklist"]},
    {"id": "brand_identity", "name": "Branding and identity", "jobs": ["brand strategy brief", "logo concept brief", "visual identity direction", "color palette", "typography pairing", "brand guidelines", "brand asset checklist", "rebrand rollout kit"]},
    {"id": "social_media", "name": "Social media content", "jobs": ["Instagram post", "Instagram story", "carousel post", "Facebook post", "LinkedIn post", "Pinterest pin", "TikTok cover", "social banner", "campaign template kit"]},
    {"id": "video_channel", "name": "Video and creator assets", "jobs": ["YouTube thumbnail", "channel banner", "video title-card brief", "stream overlay brief", "podcast cover", "episode promo graphics", "short-form video cover"]},
    {"id": "advertising", "name": "Advertising and campaigns", "jobs": ["ad creative brief", "campaign key visual", "display ad variants", "promotion graphic", "A/B creative concepts", "campaign asset matrix", "call-to-action variants"]},
    {"id": "presentations", "name": "Presentations and pitch decks", "jobs": ["pitch deck", "sales deck", "training slides", "webinar deck", "investor update", "presentation template", "speaker notes visual plan"]},
    {"id": "documents", "name": "Documents and publishing", "jobs": ["report layout", "ebook layout", "worksheet", "resume/CV layout", "case study", "proposal layout", "newsletter design", "one-page brief"]},
    {"id": "infographics", "name": "Infographics and data storytelling", "jobs": ["infographic", "process diagram brief", "comparison chart brief", "timeline graphic", "data-story layout", "research poster"]},
    {"id": "print_design", "name": "Print and event materials", "jobs": ["poster", "flyer", "brochure", "business card", "invitation", "event signage", "menu", "certificate", "print-preflight checklist"]},
    {"id": "commerce", "name": "E-commerce and product marketing", "jobs": ["product listing image brief", "product feature graphic", "storefront banner", "catalog page", "comparison sheet", "packaging concept brief", "sale/promo asset"]},
    {"id": "email_crm", "name": "Email and lifecycle marketing", "jobs": ["email header", "newsletter template", "welcome email visual", "product launch email visual", "email campaign asset set"]},
    {"id": "localization", "name": "Localization and variants", "jobs": ["language adaptation brief", "locale-specific size variants", "RTL layout review", "cultural suitability checklist", "localized campaign kit"]},
    {"id": "quality_delivery", "name": "Quality assurance and delivery", "jobs": ["contrast check plan", "visual consistency review", "content-fit review", "responsive QA checklist", "asset naming plan", "export settings checklist", "handoff package manifest", "revision summary"]},
    {"id": "photo_image_editing", "name": "Photo and image editing", "jobs": ["photo crop and resize plan", "background removal brief", "color correction brief", "image retouching checklist", "product photo cleanup", "transparent PNG asset brief", "image compression plan", "raster export checklist"]},
    {"id": "motion_video", "name": "Motion and video graphics", "jobs": ["animated title card brief", "lower-third graphics", "storyboard visual plan", "short-video captions layout", "motion poster brief", "simple animated SVG", "video overlay package", "frame-by-frame asset checklist"]},
    {"id": "illustration_vector", "name": "Illustration and vector assets", "jobs": ["SVG icon set", "vector illustration brief", "app icon family", "infographic vector shapes", "sticker sheet", "simple mascot concept", "editable diagram assets", "print-ready vector export"]},
    {"id": "3d_assets", "name": "3D and product visualization", "jobs": ["3D product render brief", "simple 3D scene plan", "lighting setup brief", "material palette", "3D icon concept", "mockup scene checklist", "camera composition plan", "render export checklist"]},
]

def get_catalog() -> list[dict[str, object]]:
    """Return a JSON-serializable copy of the catalog."""
    return [{"id": item["id"], "name": item["name"], "jobs": list(item["jobs"])} for item in CATALOG]


def search_catalog(query: str) -> list[dict[str, object]]:
    """Find categories/jobs by substring matching; suitable as a deterministic fallback."""
    terms = {part.strip().lower() for part in query.replace("/", " ").split() if len(part.strip()) > 1}
    scored: list[tuple[int, dict[str, object]]] = []
    for item in CATALOG:
        haystack = " ".join([str(item["name"]), *[str(job) for job in item["jobs"]]]).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [{"id": item["id"], "name": item["name"], "jobs": list(item["jobs"])} for _, item in scored[:5]]
