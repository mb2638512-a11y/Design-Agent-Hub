# Tool gateway and large-catalog strategy

## Two separate layers

1. **Discovery catalogs:** store/search metadata for thousands of MCP servers and API specifications without installing them. Use MCPHQ's curated JSON feed (`https://landscape.mcphq.org/api/servers.json`) and the APIs.guru OpenAPI directory (`https://api.apis.guru/v2/list.json`) as optional upstream sources. Always revalidate URLs, licenses, maintenance, and schemas before use. These sources are not a guarantee that every integration is secure or functional.
2. **Execution gateway:** use a dedicated aggregator so a compatible AI client sees one endpoint instead of dozens of child MCP servers.

## Gateway choices

| Option | Best fit | Trade-off | Source |
|---|---|---|---|
| [MetaMCP](https://github.com/metatool-ai/metamcp) | Self-hosted Docker gateway, namespaces, auth, aggregation | More services/resources; inspect current branch and requirements before deployment | MIT, verify repository license and dependencies at chosen commit |
| [devli13/mcp-gateway](https://github.com/devli13/mcp-gateway) | Small stdio gateway, one config, child process isolation | Smaller project; audit maturity and tests before production | MIT according to repository README |
| [FastMCP proxy](https://gofastmcp.com/) | Python ecosystem and proxy/aggregation patterns | Version/API compatibility must be checked | Check current project license and docs |

## Recommended design for Design-Agent-Hub

- Keep the existing Main Manager and REST API as the control plane.
- Keep the two tool catalogs separate: `mcp` for MCP servers, `api` for REST/OpenAPI services, and `builtin` for local capabilities.
- Add a gateway as a separately deployed optional service; do not embed a large aggregator into the Manager process.
- Expose only selected/approved tools to the Manager, not every discovered tool.
- Use lazy discovery and bounded tool schemas where possible; thousands of catalog records should not be injected into every model prompt.
- Keep provider credentials in a secret manager or environment, use least privilege, and do not commit real `.env` files.
- Require explicit approval for publishing, deletion, payments, account changes, and write operations.
- Treat external catalog entries as `reference_only` until smoke-tested; only verified integrations should be marked `available`.

## Connection example (illustrative, not yet tested)

Create a gateway config based on the gateway's current schema. For a simple stdio gateway, an entry may look like:

```json
{
  "mcpServers": {
    "design-agent-hub": {
      "command": "uv",
      "args": ["run", "design-agent-hub-mcp"],
      "env": {
        "DESIGN_AGENT_HUB_API_TOKEN": "${DESIGN_AGENT_HUB_API_TOKEN}"
      }
    }
  }
}
```

This example is a starting point only. Confirm the actual CLI entry point and config schema in the installed project before using it. Never put a real token directly into a committed config.

## Why not clone thousands of repositories?

Bulk cloning and auto-running thousands of third-party projects would create a large supply-chain attack surface, dependency conflicts, disk/compute costs, license obligations, and potential secret exposure. Import metadata first, select a small allowlisted set, pin reviewed versions, install in isolated environments, and test each integration. The current PR adds catalogs and gateway documentation; it does **not** claim all external servers are installed or live-verified.