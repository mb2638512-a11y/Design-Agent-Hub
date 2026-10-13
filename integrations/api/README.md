# API integrations catalog

This folder documents API references, not cloned provider implementations. Search through the list_tool_hubs(kind="api") MCP tool and review metadata in src/design_agent_hub/tool_registry.py.

## Curated starting points

| API/library | Example use | External key? | Source |
|---|---|---:|---|
| Open-Meteo | Weather/forecast data | Usually no | [Docs](https://open-meteo.com/en/docs) |
| REST Countries | Country metadata | Usually no | [Docs](https://restcountries.com/) |
| Wikipedia REST | Encyclopedia summaries | Usually no | [Docs](https://en.wikipedia.org/api/rest_v1/) |
| Open Library | Book search/metadata | Usually no | [Docs](https://openlibrary.org/developers/api) |
| PokéAPI | Demo/reference data | No | [Docs](https://pokeapi.co/docs/v2) |
| JSONPlaceholder | Mock data for testing | No | [Docs](https://jsonplaceholder.typicode.com/) |
| GitHub REST API | Repository and issue operations | Public reads may be unauthenticated; write/private access needs auth | [Docs](https://docs.github.com/en/rest) |
| Figma REST API | Design files and exports | Yes | [Docs](https://developers.figma.com/docs/rest-api/) |
| Canva Connect APIs | Design creation/export/autofill | OAuth required | [Docs](https://www.canva.dev/docs/connect/) |
| OpenAPI Generator | Generate API clients from specifications | No hosted key | [GitHub](https://github.com/OpenAPITools/openapi-generator) |
| FastAPI | Build this project's own REST API | No provider key | [GitHub](https://github.com/fastapi/fastapi) |

## How to add an API integration

1. Confirm the API terms, authentication, quotas, and data-retention rules.
2. Prefer an OpenAPI spec when one is available.
3. Add a small typed adapter with request timeout, bounded retries, error mapping, and input validation.
4. Put keys in environment variables; never return them from connector-status endpoints.
5. Add mocked tests and document which operations are read-only versus side-effecting.
6. Only label an integration available after local tests pass; catalog references are marked reference_only.

Important: no API key does not mean no network/API call. Public services are still external APIs and can have rate limits, policies, or outages. Built-in capabilities can work locally without a third-party provider key.