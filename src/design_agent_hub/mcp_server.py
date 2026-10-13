"""MCP stdio server for compatible AI agent clients."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .catalog import get_catalog, search_catalog
from .connectors.canva import CanvaConnector
from .connectors.figma import FigmaConnector
from .planner import PlanRequest, create_plan
from .figma_spec import FigmaSpecRequest, build_figma_spec
from .provider_router import recommend_tools

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
def recommend_design_tool(task: str, connected_providers: list[str] | None = None) -> str:
    """Recommend the best tool for a design task using a free-first policy. Does not execute provider actions."""
    return json.dumps(recommend_tools(task, connected_providers), ensure_ascii=False)


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
async def prepare_design_workflow(
    request: str,
    headline: str = "Ideas into editable designs",
    subheading: str = "Build, review, and refine with your workflow agent.",
    audience: str = "",
    platform: str = "",
    desired_format: str = "",
    width: int = 1080,
    height: int = 1080,
) -> str:
    """Prepare a workflow plan plus editable Figma plugin JSON. This tool does not modify provider files."""
    plan = await create_plan(
        PlanRequest(
            request=request,
            audience=audience or None,
            platform=platform or None,
            desired_format=desired_format or None,
        )
    )
    spec = build_figma_spec(
        FigmaSpecRequest(
            title=request[:100],
            headline=headline,
            subheading=subheading,
            width=width,
            height=height,
        )
    )
    return json.dumps(
        {
            "status": "prepared",
            "execution_status": "plan_only",
            "plan": plan.model_dump(),
            "figma_plugin_spec": spec,
            "next_actions": [
                "Review the plan and design spec.",
                "Paste the spec into the local Figma plugin to create editable layers.",
                "Use Canva template autofill with exact template field names for Canva assets.",
                "Ask the user before provider writes or exports.",
            ],
        },
        ensure_ascii=False,
    )

@mcp.tool()
def figma_create_plugin_spec(
    title: str = "Design Agent Hub",
    headline: str = "Ideas into editable designs",
    subheading: str = "Build, review, and refine with your workflow agent.",
    width: int = 1080,
    height: int = 1080,
    background: str = "#F8FAFC",
    accent: str = "#2563EB",
    foreground: str = "#0F172A",
    secondary: str = "#475569",
) -> str:
    """Generate a JSON spec for editable Figma layers. Paste the result into the local Figma plugin; no file is changed yet."""
    request = FigmaSpecRequest(
        title=title,
        headline=headline,
        subheading=subheading,
        width=width,
        height=height,
        background=background,
        accent=accent,
        foreground=foreground,
        secondary=secondary,
    )
    return json.dumps(build_figma_spec(request), ensure_ascii=False)

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
