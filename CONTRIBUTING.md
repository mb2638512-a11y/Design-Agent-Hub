# Contributing

1. Open an issue describing the category, workflow, or connector improvement.
2. Keep provider-specific behavior inside `connectors/`; keep planning provider-neutral.
3. Add tests for catalog matching and safety/permission boundaries.
4. Never include live tokens, private design assets, or customer data in fixtures.
5. Run `ruff check src tests` and `pytest` before submitting a pull request.
6. Clearly label operations that are plan-only versus live provider actions.
