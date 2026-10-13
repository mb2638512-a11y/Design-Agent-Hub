# Integration guide

## 1. Run locally

Install Python 3.11+, create a virtual environment, then:

```bash
pip install -e ".[dev]"
uvicorn design_agent_hub.api:app --host 127.0.0.1 --port 8000
```

The interactive API docs are at `http://127.0.0.1:8000/docs`.

## 2. Connect Penpot (free-first UI/UX option)

Penpot's official MCP integration can read and modify design files, layers, components, styles, and tokens. The Design Agent Hub router recommends Penpot for UI/UX, dashboards, wireframes, prototypes, and design systems, but it does not silently connect to or control Penpot. Follow the current [official MCP instructions](https://help.penpot.app/mcp/): enable MCP under Account → Integrations, generate and privately store the key, copy the full server URL, add it to the trusted MCP client, then open a Penpot file and use File → MCP Server → Connect. Keep the Penpot tab active while tasks run.

1. Open [Penpot MCP documentation](https://help.penpot.app/mcp/).
2. In Penpot, open **Account → Integrations → MCP Server**, enable it if available, and generate/copy the MCP URL. Treat its tokenized URL as a secret.
3. Add the provided URL to your trusted AI client as an MCP server. The URL is account-specific; do not paste it into GitHub or public issues.
4. Open the target Penpot file and use the MCP connection action in the file. Start with read-only inspection, then review any proposed edits before allowing writes.
5. If hosted MCP is unavailable for your account or client, use the documented local setup with Node.js and `npx @penpot/mcp@stable`.

Penpot is open source and its core design tools are free. Hosting, storage, connectivity, and account-level capabilities may still have limits. The Design Agent Hub does not claim to know your current Penpot quota.

## 3. Connect Figma

1. Review the [official Figma REST API authentication guide](https://developers.figma.com/docs/rest-api/authentication/).
2. For personal/local testing, create an appropriately scoped token; for multi-user integrations, prefer OAuth.
3. Store the token in a local `.env` file or secret manager as `FIGMA_ACCESS_TOKEN`.
4. Use `GET /connectors/status` to check configuration presence, then test only with a file you are authorized to access.
5. The REST adapter exposes file retrieval and node-image export URL retrieval. Export URLs are provider-generated; downloading them is a separate step. For creating editable layers, import the local plugin in `figma-plugin/` using **Plugins → Development → Import plugin from manifest…**. Generate a spec with `POST /figma/plugin-spec` or MCP `figma_create_plugin_spec`, paste it into the plugin UI, review, and run it. This avoids claiming that the Figma REST API can arbitrarily write design nodes.

## 4. Connect Canva

1. Start at the [Canva Developers SDK](https://www.canva.dev/docs/apps/).
2. Create an integration and implement the official OAuth 2.0 flow with the minimum scopes needed.
3. Store the resulting access token privately as `CANVA_ACCESS_TOKEN`.
4. Use `GET /connectors/status`, then test listing designs that the authorized user can access.
5. The REST API exposes listing, blank custom-design creation, export-job start, and export-status endpoints. Creation and export endpoints require `user_approved: true` to enforce a visible approval boundary.
6. Canva's official create-design endpoint requires `design:content:write`; export endpoints require `design:content:read`. Use the exact minimum scopes described in the official endpoint docs. Blank designs may be automatically deleted if not edited within seven days. See [create design](https://www.canva.dev/docs/apps/rest-apis/reference/designs/create-design/) and [create export job](https://www.canva.dev/docs/apps/rest-apis/reference/exports/create-design-export-job/).
7. Canva API availability, permissions, rate limits, and subscription requirements depend on the integration and endpoint.

This starter intentionally does not pretend that a token string alone completes OAuth or that every design type can be generated through a provider API.

## 5. Connect other AI agents with MCP

Run `python -m design_agent_hub.mcp_server` using the MCP client’s supported stdio configuration. Available tools:

- `list_design_categories`
- `recommend_design_tool` (free-first routing; returns suggestions only)
- `search_design_jobs`
- `plan_design_workflow`
- `figma_create_plugin_spec`
- `canva_create_autofill_job` and `canva_get_autofill_job`

Tools cover catalog/search/planning, authorized Figma file reads and node-image exports, Canva design listing, Canva blank-design creation, and Canva export jobs. Write tools require `user_approved=true`. MCP stdio should be launched only by trusted local agent clients; do not expose it to untrusted callers.

## 6. Connect over REST

- `GET /health`
- `GET /catalog`
- `GET /catalog/search?q=thumbnail`
- `POST /tools/recommend` with `{"task":"Create a responsive SaaS dashboard"}` (free-first provider routing; no external writes)
- `POST /plan`
- `GET /connectors/status`
- `POST /workflow/prepare` with a task brief and optional visual copy; returns a plan plus a paste-ready Figma spec without writing to external services
- `POST /figma/plugin-spec` with design title, headline, subheading, dimensions, and colors
- `POST /connectors/canva/autofills` with `brand_template_id`, `data`, optional `title`, and `user_approved: true`
- `GET /connectors/canva/autofills/{job_id}`
- `GET /connectors/figma/files/{file_key}`
- `POST /connectors/figma/export` with `file_key`, `node_ids`, `image_format`
- `POST /connectors/canva/designs` with `title`, `width`, `height`, `user_approved: true`
- `POST /connectors/canva/exports` with `design_id`, `file_format`, `user_approved: true`
- `GET /connectors/canva/exports/{export_id}`

Set `API_BEARER_TOKEN` before exposing the API beyond localhost and send `Authorization: Bearer <token>` on protected routes.

## 7. Optional model endpoint

Set `MODEL_BASE_URL`, `MODEL_API_KEY`, and `MODEL_NAME` for an OpenAI-compatible chat-completions endpoint. Keep keys private. If the endpoint is unavailable or returns invalid output, the planner falls back to deterministic planning.


## 8. Docker Compose

Copy `.env.example` to `.env`, generate a strong random `API_BEARER_TOKEN`, then run `docker compose up --build -d`. The compose file binds to localhost only. Do not remove that binding or expose the service publicly until TLS, rate limiting, persistent encrypted token storage, user isolation, and deployment hardening are in place.

## 9. OAuth and account setup status

The provider adapters currently accept an authorized access token from the private environment. They do not yet implement a complete multi-user OAuth callback/token-refresh service or persistent encrypted token vault. Create your own developer apps, configure only the scopes you need, and never commit tokens. For a production multi-user service, add encrypted token storage and refresh/revocation handling before offering account connections to external users.


## 10. Social platform operations

The Social Media Agent is available through `POST /manager/dispatch`. It can prepare an operating plan for accounts that you own or are authorized to manage, including platform-specific profiles, a content calendar, approval queues, moderation guidelines, and analytics.

The current agent does not sign in, create pages, publish posts, reply to messages, or fetch analytics. To enable those actions, implement and review one official platform integration at a time. Use each platform's current developer documentation, OAuth, minimum required scopes, encrypted token storage, account-owner authorization, audit logs, rate limits, and an approval step before public writes. Page/channel creation is platform-dependent and may require a manual official UI step or app review.

Never store account passwords in this project or commit access tokens. Do not automate fake engagement, unsolicited bulk messaging, or actions that bypass platform limits.
