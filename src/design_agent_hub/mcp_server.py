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


if __name__ == "__main__":
    mcp.run(transport="stdio")
