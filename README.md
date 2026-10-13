# Design Agent Hub

A provider-agnostic design workflow agent for UI/UX, brand and graphic design, content production, and agent-to-agent automation. It is designed to connect to **official Canva and Figma APIs** where the account, scopes, and plan permit, and expose reusable capabilities through a REST API and MCP tools.

> **Status: early MVP.** The REST API, design catalog, planner, MCP tools, provider adapters, and CI tests are implemented. Live provider actions still require your own valid credentials, scopes, and an end-to-end test against your Canva/Figma accounts. This repository does not bypass product restrictions or claim every task is automatable.

## What it covers

- **Product & UI/UX:** discovery briefs, user flows, information architecture, wireframes, responsive screens, prototypes, accessibility reviews, design systems, dashboards, web and mobile app interfaces.
- **Brand & identity:** logo concepts, visual identity briefs, typography/color systems, brand guidelines, asset packs.
- **Marketing & social:** social posts, ad creative briefs, YouTube thumbnails, banners, campaign kits, email graphics, landing-page creative.
- **Publishing & documents:** presentations, pitch decks, reports, infographics, ebooks, worksheets, posters, flyers, invitations, menus, resumes.
- **Commerce & business:** product listings, product graphics, storefront creative, sales sheets, catalogs, packaging concepts.
- **Production & QA:** resize/adaptation plans, localization checklists, contrast/accessibility checks, naming conventions, export checklists, delivery manifests.
- **Automation:** structured task planning, API integration boundaries, REST endpoints, MCP tools for compatible AI agents, and workflow-friendly JSON responses.

The catalog is a workflow map, not a claim that Canva or Figma can natively generate every asset type via API.

## Architecture

```text
Human / AI agent / automation
        | REST API or MCP (stdio)
        v
Design Agent Hub
  ├─ Task catalog + request planner
  ├─ Provider-neutral model adapter (optional OpenAI-compatible endpoint)
  ├─ Policy / confirmation boundary
  └─ Provider adapters
       ├─ Figma REST API
       └─ Canva Connect API
```

## Quick start

Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn design_agent_hub.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for interactive API docs. For a production deployment, set `APP_ENV=production` and a strong `API_BEARER_TOKEN` before exposing the service.

### Example request

```bash
curl -X POST http://127.0.0.1:8000/plan \
  -H "Content-Type: application/json" \
  -d '{"request":"Create a clean mobile banking dashboard UI brief","audience":"startup founders","platform":"mobile","constraints":["accessible contrast","responsive"]}'
```

### MCP server

For compatible local agent clients, configure a Python command that runs:

```bash
python -m design_agent_hub.mcp_server
```

MCP runs over stdio. Use the client’s own MCP configuration and only expose tools to trusted agents. See [integration guide](docs/INTEGRATIONS.md).

## Provider setup

- **Figma:** create an app or personal access token in Figma's developer settings. Add `FIGMA_ACCESS_TOKEN` to your private environment. OAuth is preferable for multi-user apps. Start with the [official Figma REST API docs](https://developers.figma.com/docs/rest-api/).
- **Canva:** create an integration in the Canva Developers platform and use the supported OAuth 2.0 flow/scopes. Add `CANVA_ACCESS_TOKEN` only in a local/private environment. Start with the [official Canva Developers docs](https://www.canva.dev/docs/apps/).
- **Model:** optional OpenAI-compatible endpoint settings are documented in `.env.example`. Use a model/provider you are authorized to access; no provider key is bundled.

Never commit `.env`, access tokens, OAuth client secrets, customer assets, or private design files. Rotate any credential accidentally exposed.

## Safety and reliability

- Read-only operations should be the default until a user explicitly authorizes writes.
- Require confirmation before publishing, overwriting, sharing externally, or spending paid credits.
- Use least-privilege OAuth scopes; validate all URLs and user inputs; keep logs free of secrets.
- Respect Canva/Figma terms, permissions, rate limits, copyright, and brand rights.
- Treat model output as a proposal; validate API responses and review final deliverables.
- Do not send credentials or private designs to a model unless the user has explicitly configured that behavior.

## Development

```bash
pytest
```

See [architecture](docs/ARCHITECTURE.md), [integration guide](docs/INTEGRATIONS.md), and [task catalog](src/design_agent_hub/catalog.py).

## License

MIT. Third-party services and APIs remain subject to their own terms.