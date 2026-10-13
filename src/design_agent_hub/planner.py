"""Task planning with deterministic fallback and optional OpenAI-compatible model."""

from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field

from .catalog import CATALOG, search_catalog
from .provider_router import recommend_tools


class PlanRequest(BaseModel):
    request: str = Field(min_length=3, max_length=5000)
    audience: str | None = Field(default=None, max_length=500)
    platform: str | None = Field(default=None, max_length=100)
    constraints: list[str] = Field(default_factory=list, max_length=30)
    desired_format: str | None = Field(default=None, max_length=100)
    allow_external_writes: bool = False


class DesignPlan(BaseModel):
    summary: str
    matched_categories: list[str]
    steps: list[str]
    suggested_tools: list[str]
    required_inputs: list[str]
    quality_checks: list[str]
    needs_user_confirmation_before_write: bool = True
    execution_status: str = "plan_only"


def _fallback_plan(req: PlanRequest) -> DesignPlan:
    matches = search_catalog(req.request)
    categories = [str(item["name"]) for item in matches[:3]]
    if not categories:
        categories = ["Product UI/UX", "Quality assurance and delivery"]
    routing = recommend_tools(req.request)
    tools = [str(item["name"]) for item in routing["candidates"][:3]]
    tools.insert(0, "Design Agent Hub")
    steps = [
        "Clarify the goal, audience, deliverable, dimensions, and success criteria.",
        "Choose a matching category and prepare a structured design brief.",
        "Select an authorized tool and check connector permissions before any live operation.",
        "Create or adapt the design using approved assets and brand constraints.",
        "Review accessibility, layout consistency, copy, dimensions, and export requirements.",
        "Present a preview/checklist and ask for approval before publishing or overwriting.",
    ]
    required = ["Deliverable and target dimensions", "Brand assets or reference examples (if any)"]
    if not req.audience:
        required.append("Target audience")
    if not req.platform:
        required.append("Target platform or destination")
    if not req.desired_format:
        required.append("Desired output format")
    return DesignPlan(
        summary=f"Prepare a design workflow for: {req.request}",
        matched_categories=categories,
        steps=steps,
        suggested_tools=tools,
        required_inputs=required,
        quality_checks=[
            "Readable typography and clear visual hierarchy",
            "Accessible contrast and legible text",
            "Correct platform dimensions and safe areas",
            "No unlicensed or unauthorized assets",
            "Final review and explicit approval before external publishing",
        ],
    )


async def create_plan(req: PlanRequest) -> DesignPlan:
    """Use optional configured model; safely fall back to deterministic planning."""
    base_url = os.getenv("MODEL_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv("MODEL_API_KEY", "").strip()
    model = os.getenv("MODEL_NAME", "").strip()
    if not (base_url and api_key and model):
        return _fallback_plan(req)

    catalog_names = [str(item["name"]) for item in CATALOG]
    system_prompt = (
        "You are Design Agent Hub, a professional design-workflow planner. "
        "Return only valid JSON matching keys: summary, matched_categories, steps, "
        "suggested_tools, required_inputs, quality_checks. Do not claim a design was made. "
        "Plan only; do not publish, overwrite, share, or spend money. Use only categories from "
        f"this catalog: {catalog_names}. Mention tool permissions and human approval where relevant."
    )
    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.model_dump_json()},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            import json
            content = data["choices"][0]["message"]["content"]
            plan = json.loads(content)
            return DesignPlan(**plan)
    except Exception:  # noqa: BLE001 - deterministic fallback intentionally covers provider/schema errors
        # Never leak provider errors or keys; deterministic fallback keeps the API usable.
        return _fallback_plan(req)
