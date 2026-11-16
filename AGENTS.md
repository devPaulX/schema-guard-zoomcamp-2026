# SchemaGuard agent context

SchemaGuard is a single-user educational app for validating UTF-8 CSV datasets against saved contracts. The product specification is [Issue #1](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/1). The current implementation is [Issue #2](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/2); these context documents follow [Issue #7](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/7).

## Coding rules

- Keep Python 3.12+, FastAPI, stdlib SQLite, and vanilla HTML/CSS/JavaScript. Dependencies belong in `requirements.txt`.
- Keep CSV validation deterministic and testable in `app/validation.py`. Do not edit uploaded bytes or persist CSV contents.
- Use parameterized SQL and transactions. Store local data in ignored `data/schemaguard.db`; tests use temporary databases.
- Return clear errors for invalid input and explicit reasons for contract violations. Keep names case-sensitive.
- Make focused, maintainable changes. Do not invent integrations, recovery behavior, or test evidence.
- Run `python -m pytest -q` after changes and verify the API and dashboard when changing their behavior.

## Issue-driven workflow

1. Read the relevant issue and [product specification](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/1). Keep work within that issue's scope.
2. Implement one tracked task, then check acceptance criteria and run relevant tests.
3. Report changed files, commands, results, and limitations. A QA Reviewer independently checks the result.
4. Record verification evidence on an issue only when authorized; do not close an issue based on unverified claims.

See [architecture](docs/architecture.md) and [agent roles](docs/agent-roles.md).
