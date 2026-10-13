"""MCP stdio server for compatible AI agent clients."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .catalog import get_catalog, search_catalog
from .connectors.canva import CanvaConnector
from .connectors.figma import FigmaConnector
from .planner import PlanRequest, create_plan

mcp = FastMCP("design-agent-hub")


@mcp.tool()
def list_design_categories() -> str:
    """List design categories and supported job examples."""
    return json.dumps({"categories": get_catalog()}, ensure_ascii=False)


@mcp.tool()
def search_design_jobs(query: str) -> str:
    """Search the design job catalog by category or job name."""
    return json.dumps({"query": query, "matches": search_catalog(query)}, ensure_ascii=False)


@mcp.tool()
async def plan_design_workflow(
    request: str,
    audience: str = "",
    platform: str = "",
    constraints: list[str] | None = None,
    desired_format: str = "",
) -> str:
    """Create a plan only; does not edit, publish, overwrite, or spend credits."""
    plan = await create_plan(
        PlanRequest(
            request=request,
            audience=audience or None,
            platform=platform or None,
            constraints=constraints or [],
            desired_format=desired_format or None,
        )
    )
    return plan.model_dump_json(indent=2)


@mcp.tool()
async def figma_get_file(file_key: str) -> str:
    """Read a Figma file the configured credential is authorized to access."""
    result = await FigmaConnector().get_file(file_key)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def figma_export_node_images(file_key: str, node_ids: list[str], image_format: str = "png") -> str:
    """Request image export URLs for selected nodes in an authorized Figma file."""
    result = await FigmaConnector().export_node_images(file_key, node_ids, image_format)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def canva_list_designs(limit: int = 20) -> str:
    """List Canva designs available to the configured OAuth credential."""
    result = await CanvaConnector().list_designs(limit)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def canva_create_design(title: str, width: int, height: int, user_approved: bool = False) -> str:
    """Create a blank Canva design. Set user_approved=true only after the human explicitly approves creation."""
    if not user_approved:
        return json.dumps({"status": "approval_required", "message": "Ask the user to approve creating a Canva design, then call again with user_approved=true."})
    result = await CanvaConnector().create_design(title, width, height)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def canva_start_export(design_id: str, file_format: str = "png", user_approved: bool = False) -> str:
    """Start a Canva export. Ask the human first because exports may consume provider quota."""
    if not user_approved:
        return json.dumps({"status": "approval_required", "message": "Ask the user to approve the export, then call again with user_approved=true."})
    result = await CanvaConnector().start_export(design_id, file_format)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def canva_get_export(export_id: str) -> str:
    """Check the status/result of an existing Canva export job."""
    result = await CanvaConnector().get_export(export_id)
    return json.dumps(result, ensure_ascii=False)



@mcp.tool()
async def canva_create_autofill_job(
    brand_template_id: str,
    data: dict,
    title: str = "",
    user_approved: bool = False,
) -> str:
    """Create a Canva design by filling tagged brand-template fields. Requires eligible Canva plan and user approval."""
    if not user_approved:
        return json.dumps({"status": "approval_required", "message": "Ask the user to approve creating a design from this Canva template, then call again with user_approved=true."})
    result = await CanvaConnector().create_autofill_job(brand_template_id, data, title or None)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
async def canva_get_autofill_job(job_id: str) -> str:
    """Check an existing Canva template-autofill job; successful jobs include the created design."""
    result = await CanvaConnector().get_autofill_job(job_id)
    return json.dumps(result, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="stdio")
