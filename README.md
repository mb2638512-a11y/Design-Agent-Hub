# Design Agent Hub

A provider-agnostic agent hub for design workflows, coding plans, research briefs, QA checklists, and delivery handoffs. It exposes a REST API and MCP tools and has optional official Canva/Figma adapters.

> **Status: early MVP.** The manager and six specialist agents are implemented with deterministic capability scoring. CI tests validate routing and workflow contracts. The specialists return plans/checklists, deterministic SVG and HTML starter assets, and structured starter copy; they do not autonomously complete arbitrary client jobs or guarantee polished assets. Live Canva/Figma actions still require credentials, account permissions, eligible plans, and an end-to-end test.

## Specialist team

- **Main Manager Agent:** routes a task to the best matching specialist and coordinates cross-domain requests.
- **Design Agent:** uses the 20-category / 152-example catalog and planner; can return a simple editable 1080×1080 SVG starter and a responsive single-file HTML landing-page starter for supported requests.
- **Coding Agent:** proposes implementation, testing, security, and deployment steps; does not edit repositories or run code.
- **Content Agent:** creates editable starter copy for headlines, captions, scripts, product descriptions, and campaign briefs; it does not fact-check or publish content.
- **Research Agent:** structures source-aware research; does not perform live web searches by itself.
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

Routing uses keyword/capability scoring, not autonomous reasoning. Complex cross-domain tasks can run up to three domain specialists plus Quality and Delivery in parallel. Results are proposals, not proof of external actions.

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
- A cross-domain request such as `{"task":"Research competitors, build a website, test accessibility, and deliver the complete package"}` triggers a bounded multi-agent workflow.
- MCP clients can use `list_registered_agents` and `manager_dispatch_task`.

## Design output

`POST /manager/dispatch` may include a `starter_asset` with SVG source for common static graphics. It is a generic editable starting point, not a finished brand-approved design. Save returned SVG content as a `.svg` file, HTML content as `index.html`, or copy the content starter pack into your campaign draft. Preview assets and replace placeholders before client delivery. The existing `POST /workflow/prepare` endpoint also returns a plan and Figma plugin spec, not a live Figma write.

## Official provider integrations

- **Penpot:** use the official [Penpot MCP docs](https://help.penpot.app/mcp/). Keep account-specific URLs/tokens private.
- **Figma:** use the [official Figma REST API docs](https://developers.figma.com/docs/rest-api/) and set `FIGMA_ACCESS_TOKEN` privately.
- **Canva:** use [Canva Developers](https://www.canva.dev/docs/apps/) and the supported OAuth scopes. Some template autofill features require eligible paid plans.
- **Model:** optional OpenAI-compatible endpoint settings are documented in `.env.example`; no model credentials are bundled.

Do not commit secrets, customer assets, or private design files. Require explicit user approval before publishing, overwriting, sharing externally, or spending paid credits. Respect provider terms, rate limits, licensing, and privacy.

## Development

```bash
pytest
ruff check .
```

See [integration guide](docs/INTEGRATIONS.md), [architecture](docs/ARCHITECTURE.md), and the [task catalog](src/design_agent_hub/catalog.py).

## License

MIT. Third-party services and APIs remain subject to their own terms.
