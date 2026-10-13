# Architecture

## Components

- **Catalog**: curated categories and job examples; used by API, MCP, and planner.
- **Planner**: deterministic plan generation by default. An optional OpenAI-compatible endpoint can improve plan quality. Model output is treated as untrusted data and validated against a Pydantic schema.
- **REST API**: health, catalog, search, planning, connector status.
- **MCP server**: read-only discovery and planning tools over stdio for compatible agents.
- **Provider adapters**: minimal authenticated API wrappers for authorized Figma file reads/image export and Canva design listing.

## Execution boundary

The first version deliberately plans rather than autonomously performing arbitrary edits. Publishing, sharing, overwriting, deletion, paid exports, or other consequential actions must be implemented as explicit tools with authorization, scoped credentials, idempotency, and user confirmation.

## Production hardening checklist

- Add OAuth authorization-code + PKCE flows and encrypted token storage.
- Require authentication on every non-health endpoint before network exposure.
- Add rate limiting, request-size limits, structured redacted logs, and audit events.
- Add per-user/provider permission checks and token refresh/revocation handling.
- Use queues for long jobs; persist job status and retry safely.
- Add integration tests against provider sandboxes and schema/contract tests.
- Keep model prompts, assets, and API responses out of logs unless explicitly needed.
- Add human approval for external publishing and destructive changes.
