# Integration guide

## 1. Run locally

Install Python 3.11+, create a virtual environment, then:

```bash
pip install -e ".[dev]"
uvicorn design_agent_hub.api:app --host 127.0.0.1 --port 8000
```

The interactive API docs are at `http://127.0.0.1:8000/docs`.

## 2. Connect Figma

1. Review the [official Figma REST API authentication guide](https://developers.figma.com/docs/rest-api/authentication/).
2. For personal/local testing, create an appropriately scoped token; for multi-user integrations, prefer OAuth.
3. Store the token in a local `.env` file or secret manager as `FIGMA_ACCESS_TOKEN`.
4. Use `GET /connectors/status` to check configuration presence, then test only with a file you are authorized to access.
5. The adapter currently exposes file retrieval and node-image export URL retrieval. Export URLs are provider-generated; downloading them is a separate step.

## 3. Connect Canva

1. Start at the [Canva Developers SDK](https://www.canva.dev/docs/apps/).
2. Create an integration and implement the official OAuth 2.0 flow with the minimum scopes needed.
3. Store the resulting access token privately as `CANVA_ACCESS_TOKEN`.
4. Use `GET /connectors/status`, then test listing designs that the authorized user can access.
5. The REST API exposes listing, blank custom-design creation, export-job start, and export-status endpoints. Creation and export endpoints require `user_approved: true` to enforce a visible approval boundary.
6. Canva's official create-design endpoint requires `design:content:write`; export endpoints require `design:content:read`. Use the exact minimum scopes described in the official endpoint docs. Blank designs may be automatically deleted if not edited within seven days. See [create design](https://www.canva.dev/docs/apps/rest-apis/reference/designs/create-design/) and [create export job](https://www.canva.dev/docs/apps/rest-apis/reference/exports/create-design-export-job/).
7. Canva API availability, permissions, rate limits, and subscription requirements depend on the integration and endpoint.

This starter intentionally does not pretend that a token string alone completes OAuth or that every design type can be generated through a provider API.

## 4. Connect other AI agents with MCP

Run `python -m design_agent_hub.mcp_server` using the MCP client’s supported stdio configuration. Available tools:

- `list_design_categories`
- `search_design_jobs`
- `plan_design_workflow`

Tools cover catalog/search/planning, authorized Figma file reads and node-image exports, Canva design listing, Canva blank-design creation, and Canva export jobs. Write tools require `user_approved=true`. MCP stdio should be launched only by trusted local agent clients; do not expose it to untrusted callers.

## 5. Connect over REST

- `GET /health`
- `GET /catalog`
- `GET /catalog/search?q=thumbnail`
- `POST /plan`
- `GET /connectors/status`
- `GET /connectors/figma/files/{file_key}`
- `POST /connectors/figma/export` with `file_key`, `node_ids`, `image_format`
- `POST /connectors/canva/designs` with `title`, `width`, `height`, `user_approved: true`
- `POST /connectors/canva/exports` with `design_id`, `file_format`, `user_approved: true`
- `GET /connectors/canva/exports/{export_id}`

Set `API_BEARER_TOKEN` before exposing the API beyond localhost and send `Authorization: Bearer <token>` on protected routes.

## 6. Optional model endpoint

Set `MODEL_BASE_URL`, `MODEL_API_KEY`, and `MODEL_NAME` for an OpenAI-compatible chat-completions endpoint. Keep keys private. If the endpoint is unavailable or returns invalid output, the planner falls back to deterministic planning.
