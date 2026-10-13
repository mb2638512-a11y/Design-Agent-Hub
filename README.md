# Design Agent Hub

A **frontend-free MCP server** that gives compatible AI agents extra tools for design workflows, coding plans, research, social-platform planning, QA, and delivery. MCP is the primary interface; an optional REST API is also available.

> **Status: early MVP.** The manager and seven specialist agents are implemented with deterministic capability scoring. CI tests validate routing and workflow contracts. The specialists return plans/checklists, deterministic SVG and HTML starter assets, and structured starter copy; they do not autonomously complete arbitrary client jobs or guarantee polished assets. Live Canva/Figma and social platform actions still require credentials, account permissions, eligible plans, and end-to-end tests.

## Specialist team

- **Main Manager Agent:** routes a task to the best matching specialist and coordinates cross-domain requests.
- **Design Agent:** uses the 20-category / 152-example catalog and planner; can return a simple editable 1080×1080 SVG starter and a responsive single-file HTML landing-page starter for supported requests.
- **Coding Agent:** proposes implementation, testing, security, and deployment steps; does not edit repositories or run code.
- **Content Agent:** creates editable starter copy for headlines, captions, scripts, product descriptions, and campaign briefs; it does not fact-check or publish content.
- **Research Agent:** structures source-aware research; does not perform live web searches by itself.
- **Social Media Agent:** plans owned-account setup, content calendars, approved publishing, moderation, and analytics. Live actions require authorized connectors and account-owner approval.
- **Quality Agent:** returns review gates for correctness, accessibility, privacy, and delivery; does not claim checks actually ran.
- **Delivery Agent:** prepares a handoff manifest; does not upload, email, publish, or export files itself.

## Architecture

```text
Human / automation / compatible AI client
              | REST API or MCP (stdio)
              v
       Main Manager Agent
              |
        Agent Registry
              |
   +----------+-----------+----------+-----------+
   |          |           |          |           |
 Design     Coding     Content     Research    Quality    Delivery
   |          |           |          |           |
 plan +     build plan   evidence   QA gates   handoff
 SVG draft               workflow              manifest
```

Routing uses deterministic capability scoring rather than unconstrained autonomous reasoning. The manager now creates an explicit task plan, assigns up to three domain specialists for complex work, runs QA against their actual returned results, then prepares a delivery handoff, enforces per-agent timeouts, validates result structure, applies a narrow metadata-only self-repair, and preserves partial successes. Structural QA does not prove factual accuracy or visual quality. An optional local SQLite memory stores compact task summaries only when explicitly enabled. The planner can use a configured primary OpenAI-compatible model, then an optional fallback model, then deterministic planning.

## MCP first — no frontend

There is no web UI to open. Add this server to an MCP-compatible client and the client can discover and call its tools. The server exposes manager dispatch, specialist discovery, design-job search, workflow planning, Canva/Figma operations (when credentials are configured), and a social-platform capability catalog. Read [the MCP setup guide](docs/DEPLOYMENT.md) for client configuration. MCP tools do not magically grant provider access: Canva/Figma credentials, provider scopes, account permissions, and human approval are still required for protected actions.

## Quick start

Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
uvicorn design_agent_hub.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`. In production, set `APP_ENV=production` and a strong `API_BEARER_TOKEN` before exposing the service.

## Manager API

- `GET /agents` lists registered specialists and routing mode.
- `POST /manager/dispatch` with `{"task":"Create an Instagram post design"}` routes a task.
- `POST /artifacts/download` with `{"task":"Create an Instagram post","file_format":"svg"}` or `{"task":"Create a landing page","file_format":"html"}` returns a downloadable starter file.
- `POST /artifacts/package` with `{"task":"Create a launch campaign"}` returns a ZIP with editable HTML/SVG starters, a content brief, README, and manifest.
- A cross-domain request such as `{"task":"Research competitors, build a website, test accessibility, and deliver the complete package"}` triggers a bounded multi-agent workflow.
- MCP clients can use `list_registered_agents`, `manager_dispatch_task`, `list_design_categories`, `search_design_jobs`, `recommend_design_tool`, `plan_design_workflow`, `prepare_design_workflow`, and `list_supported_social_platforms`; Canva/Figma tools are available when configured.

## Design output

`POST /manager/dispatch` may include a `starter_asset` with SVG source for common static graphics. It is a generic editable starting point, not a finished brand-approved design. Use `POST /artifacts/download` to download an editable SVG or HTML starter directly, or `POST /artifacts/package` to download a ZIP containing both starters, a content brief, and a manifest. You can also save returned SVG content as a `.svg` file, HTML content as `index.html`, or copy the content starter pack into your campaign draft. Preview assets and replace placeholders before client delivery. The existing `POST /workflow/prepare` endpoint also returns a plan and Figma plugin spec, not a live Figma write.

## Social media agent

The Social Media Agent plans workflows for Facebook Pages, Instagram, YouTube, TikTok, LinkedIn Pages, Pinterest, Threads, and X. `GET /social/platforms` returns the supported-platform catalog, setup constraints, and shared workflow. See [the social media implementation roadmap](docs/SOCIAL_MEDIA_ROADMAP.md). The catalog is not a live connection: account inventory, OAuth, publishing, moderation, and analytics require approved provider integrations and secure per-user authorization.

## Official provider integrations

- **Penpot:** use the official [Penpot MCP docs](https://help.penpot.app/mcp/). Keep account-specific URLs/tokens private.
- **Figma:** use the [official Figma REST API docs](https://developers.figma.com/docs/rest-api/) and set `FIGMA_ACCESS_TOKEN` privately.
- **Canva:** use [Canva Developers](https://www.canva.dev/docs/apps/) and the supported OAuth scopes. Some template autofill features require eligible paid plans.
- **Model:** optional OpenAI-compatible endpoint settings are documented in `.env.example`; no model credentials are bundled.

Do not commit secrets, customer assets, or private design files. Require explicit user approval before publishing, overwriting, sharing externally, or spending paid credits. Respect provider terms, rate limits, licensing, and privacy.

## Manager reliability, memory, and model failover

- Set `MODEL_BASE_URL`, `MODEL_API_KEY`, and `MODEL_NAME` for the primary OpenAI-compatible chat-completions endpoint.
- Optionally set `MODEL_FALLBACK_BASE_URL`, `MODEL_FALLBACK_API_KEY`, and `MODEL_FALLBACK_NAME`. If the primary fails or returns an invalid response, the planner tries the fallback, then uses its deterministic planner.
- Local task memory is **off by default**. To enable it, set `MANAGER_MEMORY_ENABLED=true` and optionally `MANAGER_MEMORY_PATH` to a private local path. It stores at most 100 task strings (bounded to 2,000 characters) plus compact status/agent summaries—not full specialist outputs. MCP tools `manager_recent_task_memory` and `manager_clear_task_memory` provide read/delete controls; deletion requires explicit approval. Keep the database private and disable memory if tasks may contain secrets or sensitive data.
- The manager's structural self-repair can add missing agent identity metadata only. It does not silently rewrite task content or claim semantic/factual verification. Failed agents are reported for targeted retry; automatic retries are avoided to reduce duplicate external side effects.

## Development

```bash
pytest
ruff check .
```

See [integration guide](docs/INTEGRATIONS.md), [architecture](docs/ARCHITECTURE.md), and the [task catalog](src/design_agent_hub/catalog.py).

## License

MIT. Third-party services and APIs remain subject to their own terms.


## Separate MCP and API tool hubs

The repository now has two curated integration folders: [MCP references](integrations/mcp/README.md) and [API references](integrations/api/README.md). The catalog is searchable from compatible MCP clients through `list_tool_hubs(kind="mcp" | "api" | "builtin")` and `search_tool_hubs(query, kind)`. The authenticated REST API exposes the same catalog at `GET /tools/catalog?kind=mcp|api|builtin&no_key_only=true` and `GET /tools/catalog/search?q=browser&kind=mcp`.

The current registry contains **12 MCP reference entries**, **12 API/library reference entries**, and **14 built-in capabilities** that do not require a third-party provider API key. The built-ins include manager routing, agent discovery, local design catalog/search, tool recommendations, workflow planning, Figma plugin-spec generation, SVG/HTML starter generation, content drafts, QA checklists, delivery manifests, local ZIP packaging, and opt-in local task memory.

**Important distinction:** the directories are curated references; third-party repositories have not been cloned or installed into this project, and integrations marked `reference_only` are not connected. The existing Canva and Figma adapters are only partially integrated and need credentials, correct scopes, and end-to-end verification. “No external API key” also does not mean “no MCP”: built-ins can be called through this project's REST API without an MCP client, while an MCP-compatible client uses the MCP server. Public third-party APIs still require network access and can impose rate limits.

Run `pytest -q` to verify the catalog tests after installing the development dependencies.
