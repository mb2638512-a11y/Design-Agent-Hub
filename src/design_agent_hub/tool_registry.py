"""Curated tool directory for local capabilities, MCP servers, and HTTP APIs.

This is a metadata catalog, not an installer. Third-party repositories are never
cloned or executed automatically. Verify licenses, security, and provider terms
before installing or connecting any external integration.
"""
from __future__ import annotations

from typing import Any

BUILTIN_TOOLS: list[dict[str, Any]] = [
    {"id": "manager_dispatch", "name": "Main Manager task routing", "kind": "builtin", "purpose": "Route a task to registered specialist agents and return a structured report.", "needs_mcp": False, "needs_external_api_key": False, "status": "available", "note": "Can use deterministic fallback; model configuration is optional."},
    {"id": "agent_discovery", "name": "Specialist discovery", "kind": "builtin", "purpose": "List registered agents and their capabilities.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "design_catalog", "name": "Design category catalog", "kind": "builtin", "purpose": "Browse supported design categories and example jobs.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "design_search", "name": "Design job search", "kind": "builtin", "purpose": "Search local design-job examples by keyword.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "tool_recommendation", "name": "Free-first tool recommendation", "kind": "builtin", "purpose": "Recommend a suitable tool from task keywords and connected-provider hints.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "workflow_planning", "name": "Workflow planning", "kind": "builtin", "purpose": "Build a structured design workflow plan.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "figma_plugin_spec", "name": "Editable Figma plugin spec", "kind": "builtin", "purpose": "Generate JSON instructions for editable layers without calling Figma.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "svg_starter", "name": "SVG starter asset", "kind": "builtin", "purpose": "Create an editable local SVG starter for supported requests.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "html_starter", "name": "HTML landing-page starter", "kind": "builtin", "purpose": "Create a responsive single-file HTML starter for supported requests.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "content_draft", "name": "Content starter copy", "kind": "builtin", "purpose": "Draft captions, headlines, scripts, product copy, and briefs.", "needs_mcp": False, "needs_external_api_key": False, "status": "available", "note": "Generated content is not automatically fact-checked or published."},
    {"id": "quality_checklist", "name": "Quality checklist", "kind": "builtin", "purpose": "Prepare accessibility, privacy, correctness, and delivery review gates.", "needs_mcp": False, "needs_external_api_key": False, "status": "available", "note": "Checklist generation is not proof that tests ran."},
    {"id": "delivery_manifest", "name": "Delivery handoff manifest", "kind": "builtin", "purpose": "Prepare a delivery checklist and handoff manifest.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "artifact_package", "name": "Local starter package", "kind": "builtin", "purpose": "Package supported starter artifacts and brief into a ZIP.", "needs_mcp": False, "needs_external_api_key": False, "status": "available"},
    {"id": "task_memory", "name": "Opt-in local task memory", "kind": "builtin", "purpose": "Store and read compact task summaries in local SQLite.", "needs_mcp": False, "needs_external_api_key": False, "status": "available", "note": "Disabled by default; set MANAGER_MEMORY_ENABLED=true to opt in."},
]

MCP_CATALOG: list[dict[str, Any]] = [
    {"id": "mcp-filesystem", "name": "Filesystem MCP Server", "purpose": "Read/write files in explicitly allowed local directories.", "repository": "https://github.com/modelcontextprotocol/servers", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only", "safety": "Restrict allowed directories; do not expose secrets or the whole home directory."},
    {"id": "mcp-memory", "name": "Memory MCP Server", "purpose": "Knowledge-graph style memory for compatible clients.", "repository": "https://github.com/modelcontextprotocol/servers", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "mcp-fetch", "name": "Fetch MCP Server", "purpose": "Fetch and convert public web pages to text.", "repository": "https://github.com/modelcontextprotocol/servers", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only", "safety": "Public web fetch is not a guarantee of unrestricted access or reliable facts."},
    {"id": "mcp-github", "name": "GitHub MCP Server", "purpose": "Interact with GitHub repositories, issues, and pull requests.", "repository": "https://github.com/github/github-mcp-server", "needs_mcp": True, "needs_external_api_key": True, "status": "reference_only", "safety": "Use a least-privilege GitHub token; write actions need approval."},
    {"id": "mcp-playwright", "name": "Playwright MCP", "purpose": "Browser automation and web UI testing.", "repository": "https://github.com/microsoft/playwright-mcp", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only", "safety": "Browser sessions can access signed-in accounts; use a test profile."},
    {"id": "mcp-context7", "name": "Context7 MCP", "purpose": "Retrieve current library documentation for coding tasks.", "repository": "https://github.com/upstash/context7", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "mcp-sqlite", "name": "SQLite MCP Server", "purpose": "Query a permitted local SQLite database.", "repository": "https://github.com/modelcontextprotocol/servers", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only", "safety": "Prefer read-only database access until write permissions are explicitly needed."},
    {"id": "mcp-time", "name": "Time MCP Server", "purpose": "Time and timezone utilities.", "repository": "https://github.com/modelcontextprotocol/servers", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "mcp-brave-search", "name": "Brave Search MCP", "purpose": "Search the web through Brave Search.", "repository": "https://github.com/modelcontextprotocol/servers", "needs_mcp": True, "needs_external_api_key": True, "status": "reference_only", "safety": "Requires a provider key and is subject to provider quotas."},
    {"id": "mcp-sequential-thinking", "name": "Sequential Thinking MCP", "purpose": "Expose a structured step-by-step thinking tool to compatible clients.", "repository": "https://github.com/modelcontextprotocol/servers", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "mcp-penpot", "name": "Penpot MCP", "purpose": "Connect supported design workflows to Penpot.", "repository": "https://help.penpot.app/mcp/", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only", "note": "Check current setup and account requirements before connecting."},
    {"id": "mcp-gateway", "name": "MCP Gateway / aggregator", "purpose": "Combine multiple MCP servers or API sources behind a controlled endpoint.", "repository": "https://github.com/unrelated-ai/mcp-gateway", "needs_mcp": True, "needs_external_api_key": False, "status": "reference_only", "safety": "Gateway security, authentication, allowlists, and secret storage must be configured."},
]

API_CATALOG: list[dict[str, Any]] = [
    {"id": "api-open-meteo", "name": "Open-Meteo", "purpose": "Weather and forecast data.", "documentation": "https://open-meteo.com/en/docs", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only", "limits": "Review current fair-use limits and attribution requirements."},
    {"id": "api-rest-countries", "name": "REST Countries", "purpose": "Country names, regions, flags, and basic country metadata.", "documentation": "https://restcountries.com/", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "api-wikipedia", "name": "Wikipedia REST API", "purpose": "Retrieve encyclopedia summaries and page content.", "documentation": "https://en.wikipedia.org/api/rest_v1/", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only", "limits": "Respect Wikimedia API policies and identify sources."},
    {"id": "api-open-library", "name": "Open Library", "purpose": "Search books and retrieve bibliographic metadata.", "documentation": "https://openlibrary.org/developers/api", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "api-pokeapi", "name": "PokéAPI", "purpose": "Retrieve Pokémon reference data for demos and examples.", "documentation": "https://pokeapi.co/docs/v2", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "api-jsonplaceholder", "name": "JSONPlaceholder", "purpose": "Mock REST endpoints for development and integration tests.", "documentation": "https://jsonplaceholder.typicode.com/", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only", "note": "Demo data only; not a production data source."},
    {"id": "api-github", "name": "GitHub REST API", "purpose": "Repository, issue, and pull-request operations.", "documentation": "https://docs.github.com/en/rest", "needs_mcp": False, "needs_external_api_key": True, "status": "reference_only", "note": "Some public read operations may work unauthenticated with stricter limits; private/write operations require auth."},
    {"id": "api-figma", "name": "Figma REST API", "purpose": "Read files and request node image exports.", "documentation": "https://developers.figma.com/docs/rest-api/", "needs_mcp": False, "needs_external_api_key": True, "status": "partially_integrated", "note": "Existing connector supports configured Figma credentials; verify scopes and current API permissions."},
    {"id": "api-canva", "name": "Canva Connect APIs", "purpose": "Create designs, export, and fill eligible templates.", "documentation": "https://www.canva.dev/docs/connect/", "needs_mcp": False, "needs_external_api_key": True, "status": "partially_integrated", "note": "Existing connector requires OAuth setup, scopes, account eligibility, and user approval for writes/exports."},
    {"id": "api-openlibrary-search", "name": "Open Library Search", "purpose": "Search book records without building a new backend.", "documentation": "https://openlibrary.org/dev/docs/api/search", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only"},
    {"id": "api-openapi-generator", "name": "OpenAPI Generator", "purpose": "Generate typed API clients and server stubs from OpenAPI descriptions.", "documentation": "https://github.com/OpenAPITools/openapi-generator", "needs_mcp": False, "needs_external_api_key": False, "status": "reference_only", "note": "A local code generator, not a hosted data API."},
    {"id": "api-fastapi", "name": "FastAPI", "purpose": "Build and document this project's own REST API.", "documentation": "https://github.com/fastapi/fastapi", "needs_mcp": False, "needs_external_api_key": False, "status": "available", "note": "Already used by Design Agent Hub."},
]


def list_tool_catalog(kind: str | None = None, no_key_only: bool = False) -> dict[str, Any]:
    """Return built-in capabilities and curated integration references."""
    groups = {"builtin": BUILTIN_TOOLS, "mcp": MCP_CATALOG, "api": API_CATALOG}
    if kind and kind not in groups:
        return {"error": "kind must be one of: builtin, mcp, api", "available_kinds": list(groups)}
    selected = {kind: groups[kind]} if kind else groups
    result: dict[str, Any] = {}
    for group, items in selected.items():
        result[group] = [
            item for item in items
            if not no_key_only or not item.get("needs_external_api_key", False)
        ]
    return {
        "counts": {group: len(items) for group, items in result.items()},
        "total": sum(len(items) for items in result.values()),
        "no_external_api_key_count": sum(
            1 for items in result.values() for item in items
            if not item.get("needs_external_api_key", False)
        ),
        "catalog_is_metadata_not_installation": True,
        "items": result,
    }


def search_tool_catalog(query: str, kind: str | None = None) -> list[dict[str, Any]]:
    """Search the curated catalog by name, purpose, or tags."""
    q = query.strip().casefold()
    if not q:
        return []
    catalog = list_tool_catalog(kind=kind)
    if "error" in catalog:
        return []
    return [
        item for items in catalog["items"].values() for item in items
        if q in " ".join(str(value) for value in item.values()).casefold()
    ][:50]


CATALOG_SOURCES: list[dict[str, Any]] = [
    {
        "id": "mcphq-landscape",
        "kind": "mcp",
        "name": "MCPHQ Awesome MCP Servers",
        "url": "https://landscape.mcphq.org/api/servers.json",
        "repository": "https://github.com/mcpHQ/awesome-mcp-servers",
        "purpose": "Curated structured metadata for discovering MCP servers.",
        "sync_mode": "explicit_opt_in_only",
        "verified_by_this_project": False,
    },
    {
        "id": "apis-guru-openapi-directory",
        "kind": "api",
        "name": "APIs.guru OpenAPI Directory",
        "url": "https://api.apis.guru/v2/list.json",
        "repository": "https://github.com/APIs-guru/openapi-directory",
        "purpose": "Discover public API specifications for possible client generation.",
        "sync_mode": "explicit_opt_in_only",
        "verified_by_this_project": False,
    },
]


def list_catalog_sources() -> list[dict[str, Any]]:
    """Return upstream metadata catalog feeds; does not fetch or trust them automatically."""
    return [dict(source) for source in CATALOG_SOURCES]
