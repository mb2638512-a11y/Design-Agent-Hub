# MCP integrations catalog

This folder documents references, not vendored or auto-executed third-party code. The searchable metadata is exposed by the list_tool_hubs(kind="mcp") MCP tool and stored in src/design_agent_hub/tool_registry.py.

## Curated starting points

| Integration | Use | External key? | Source |
|---|---|---:|---|
| Filesystem MCP | Local files in explicitly allowed directories | Usually no | [MCP servers](https://github.com/modelcontextprotocol/servers) |
| Memory MCP | Knowledge-graph memory | Usually no | [MCP servers](https://github.com/modelcontextprotocol/servers) |
| Fetch MCP | Retrieve public web pages | Usually no | [MCP servers](https://github.com/modelcontextprotocol/servers) |
| GitHub MCP | Repositories, issues, PRs | Yes for private/write access | [GitHub MCP](https://github.com/github/github-mcp-server) |
| Playwright MCP | Browser automation and testing | No provider key, but browser session access is sensitive | [Playwright MCP](https://github.com/microsoft/playwright-mcp) |
| Context7 | Library documentation lookup | Check current service terms | [Context7](https://github.com/upstash/context7) |
| SQLite MCP | Query an allowed local database | Usually no | [MCP servers](https://github.com/modelcontextprotocol/servers) |
| Time MCP | Time/timezone helpers | No | [MCP servers](https://github.com/modelcontextprotocol/servers) |
| Brave Search MCP | Web search | Yes | [MCP servers](https://github.com/modelcontextprotocol/servers) |
| Sequential Thinking MCP | Structured planning helper | No | [MCP servers](https://github.com/modelcontextprotocol/servers) |
| Penpot MCP | Design integration | Verify current setup | [Penpot MCP docs](https://help.penpot.app/mcp/) |
| MCP Gateway | Aggregate MCP/API sources | Depends on upstream services | [unrelated-ai/mcp-gateway](https://github.com/unrelated-ai/mcp-gateway) |

## Safe installation policy

1. Review repository license, recent maintenance, dependency tree, and security advisories.
2. Pin a reviewed commit or release; avoid running remote packages without inspection.
3. Store credentials in environment variables or a secret manager, never in source control.
4. Restrict filesystem roots, browser profiles, network access, and tool permissions.
5. Keep read-only access as the default; ask before publishing, deleting, exporting, spending credits, or changing accounts.
6. Install and connect one integration at a time, then run a smoke test.

Important: listing a server here does not mean it has been cloned, installed, connected, or verified in this repository.