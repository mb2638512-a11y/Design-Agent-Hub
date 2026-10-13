# Install and connect Design Agent Hub MCP

Design Agent Hub is a **frontend-free MCP server**. You connect it to an MCP-compatible AI client; there is no website or dashboard to open. The simplest and safest option is local **stdio** transport.

## Requirements

- Python 3.11 or newer
- Git
- An MCP-compatible client (for example, Claude Desktop, Cursor, or another client that supports local MCP servers)

## 1. Install

```bash
git clone https://github.com/mb2638512-a11y/Design-Agent-Hub.git
cd Design-Agent-Hub
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -e .
```

## 2. Configure your MCP client

The server entry point is `design_agent_hub.mcp_server`. Configure your MCP client to launch it using the same Python environment where the package was installed.

Example MCP configuration for clients that use a JSON `mcpServers` object (replace the path with your absolute repository path):

```json
{
  "mcpServers": {
    "design-agent-hub": {
      "command": "python",
      "args": ["-m", "design_agent_hub.mcp_server"],
      "cwd": "/absolute/path/to/Design-Agent-Hub"
    }
  }
}
```

If your client does not support `cwd`, use the absolute path to that environment's Python executable and ensure the package was installed with `pip install -e .`. Restart or reload the MCP client, then ask it to list the tools from **design-agent-hub**.

## 3. MCP tools

- `list_registered_agents` — discover the manager and specialists.
- `manager_dispatch_task` — route a task to a specialist workflow.
- `list_design_categories` and `search_design_jobs` — discover supported design jobs.
- `recommend_design_tool` — choose a tool using free-first recommendations.
- `plan_design_workflow` and `prepare_design_workflow` — prepare a plan/spec.
- `list_supported_social_platforms` — inspect the supported social platform catalog and integration readiness.
- Canva/Figma tools — list or operate on resources permitted by configured credentials; creation/export actions require approval flags.

## 4. Configure provider credentials only if needed

Copy `.env.example` to `.env` and add only credentials for providers you personally control and are authorized to access. Never commit `.env` or paste secrets into prompts. The server does not provide shared accounts, shared OAuth tokens, or free paid-plan access.

## Current limits and safety

- The server is MCP-first and has no frontend. A REST API remains available as an optional interface.
- Specialist routing is deterministic capability matching, not a separate autonomous frontier model.
- Some tools produce plans or starter specs rather than completing every task end-to-end.
- Social platforms are currently a capability/readiness catalog, not connected accounts; OAuth, publishing, comments, scheduling, and analytics integrations still need provider-specific implementation and approval.
- Do not expose a remote MCP endpoint publicly without authentication and transport security. Local stdio is the default and safest setup.
- External writes, publishing, exports, and actions that can consume quota require explicit approval where supported.
