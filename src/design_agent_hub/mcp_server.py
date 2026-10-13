"""MCP stdio server for compatible AI agent clients."""

from __future__ import annotations

import asyncio
import json

from mcp.server.fastmcp import FastMCP

from .catalog import get_catalog, search_catalog
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


if __name__ == "__main__":
    mcp.run(transport="stdio")
