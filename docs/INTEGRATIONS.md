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
5. Canva API availability, permissions, rate limits, and subscription requirements depend on the integration and endpoint.

This starter intentionally does not pretend that a token string alone completes OAuth or that every design type can be generated through a provider API.

## 4. Connect other AI agents with MCP

Run `python -m design_agent_hub.mcp_server` using the MCP client’s supported stdio configuration. Available tools:

- `list_design_categories`
- `search_design_jobs`
- `plan_design_workflow`

These tools provide catalog and planning only. They do not perform live writes. Do not expose an unauthenticated MCP process to untrusted callers.

## 5. Connect over REST

- `GET /health`
- `GET /catalog`
- `GET /catalog/search?q=thumbnail`
- `POST /plan`
- `GET /connectors/status`

Set `API_BEARER_TOKEN` before exposing the API beyond localhost and send `Authorization: Bearer <token>` on protected routes.

## 6. Optional model endpoint

Set `MODEL_BASE_URL`, `MODEL_API_KEY`, and `MODEL_NAME` for an OpenAI-compatible chat-completions endpoint. Keep keys private. If the endpoint is unavailable or returns invalid output, the planner falls back to deterministic planning.
