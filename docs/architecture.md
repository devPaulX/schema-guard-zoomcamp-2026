# SchemaGuard architecture

The [product specification (Issue #1)](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/1) defines a broader roadmap. [Issue #2](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/2) delivers contract management and CSV validation; [Issue #7](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/7) defines agent context.

## Components

- `app/main.py`: FastAPI entrypoint `app.main:app`, request validation, API routes, and static frontend serving.
- `app/validation.py`: pure CSV parsing and contract rules. It checks UTF-8, size, headers, row widths, and per-column missing percentages.
- `app/database.py`: SQLite connection, schema creation, and parameterized contract and history queries.
- `frontend/`: HTML, CSS, and JavaScript dashboard using the same-origin REST API.
- `tests/`: unit tests for CSV rules and integration tests for API, SQLite persistence, and frontend delivery.

The client creates a contract through JSON, then submits a multipart CSV and contract ID. The server reads at most 5 MiB plus one byte, validates without changing the upload, and stores status, reasons, filename, contract reference, and UTC timestamp. Invalid CSV requests return an error and do not create a history record. Contract-rule failures create a `FAIL` record. The database lives at `data/schemaguard.db` and is ignored by Git.

There is no authentication, automated header repair, incident response, deployment, or external service in the Issue #2 slice. Those broader specification capabilities require their own tracked work.
