# SchemaGuard

[![CI](https://github.com/devPaulX/schema-guard-zoomcamp-2026/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/devPaulX/schema-guard-zoomcamp-2026/actions/workflows/ci.yml)

SchemaGuard checks UTF-8 CSV datasets against saved contracts and keeps validation history. This is the contract validation slice of the [product specification (Issue #1)](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/1), implemented for [Issue #2](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/2). Browser tests and the Docker runtime follow [Issue #3](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/3). Agent context follows [Issue #7](https://github.com/devPaulX/schema-guard-zoomcamp-2026/issues/7).



   ## Live Application

   **Deployment:** Render (Docker)

   - [Live Dashboard](https://schemaguard-2026.onrender.com/)
   - [Interactive API Documentation](https://schemaguard-2026.onrender.com/docs)
   - [Health Check](https://schemaguard-2026.onrender.com/api/health)
   - [GitHub CI](https://github.com/devPaulX/schema-guard-zoomcamp-2026/actions)
   - [Deployment and Rollback Guide](docs/deployment.md)

   ### Deployment Status

   - Public HTTPS application deployed successfully.
   - FastAPI backend and frontend operational.
   - CSV contract creation and validation verified.
   - CI pipeline successfully executed.
   - Docker Compose supports persistent local SQLite storage.

   **Note:** Render Free uses ephemeral storage.
   Data may be lost when the instance restarts or redeploys.
   The public deployment is intended for demonstration only.
   Do not upload sensitive datasets.
   

## Requirements and setup

Python 3.12 or newer. Run these PowerShell commands from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/> for the dashboard and <http://127.0.0.1:8000/docs> for interactive API documentation. Contracts and results persist in the ignored `data/schemaguard.db` file.

The Playwright installation downloads headless Chromium once. Run the complete suite, including the real browser smoke test, from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

For other shells, create a Python 3.12+ virtual environment and use its `python -m pip install -r requirements.txt`, `python -m playwright install chromium`, `python -m uvicorn app.main:app --reload`, and `python -m pytest -q` commands. On Linux, install any missing Chromium system libraries with `python -m playwright install --with-deps chromium`.

## Docker Compose

With Docker running, start the complete application from the repository root:

```sh
docker compose up --build -d
docker compose ps
```

Open <http://127.0.0.1:8000/> for the dashboard, <http://127.0.0.1:8000/docs> for API documentation, and <http://127.0.0.1:8000/api/health> for health status. Compose maps port 8000 and mounts the named `schemaguard_data` volume at `/app/data`. SQLite is stored at `/app/data/schemaguard.db`; uploaded CSV contents are never stored.

Restart the container and confirm that contracts and validation history remain available:

```sh
docker compose restart
docker compose ps
```

Stop the application without deleting the database volume:

```sh
docker compose down
```

The volume also survives a later `docker compose up --build -d`. A local `data/schemaguard.db` and the Docker volume are separate data stores. `docker compose down --volumes` deletes the Docker database and should only be used when intentionally discarding it. See the [deployment and rollback guide](docs/deployment.md) for Render and persistent local Docker procedures.

## Deployment verification checklist

- [ ] The `CI / test-and-build` check passes for the deployed `main` commit, including the Chromium browser test and Docker build.
- [ ] Render auto-deploy is set to **After CI Checks Pass**, and the live deploy shows that commit.
- [ ] The public `/api/health` endpoint returns HTTP 200 and `{"status":"ok"}`; the dashboard loads over HTTPS.
- [ ] A disposable contract, CSV validation result, and history entry appear in the public dashboard.
- [ ] A previous successful deploy can be restored using the [rollback steps](docs/deployment.md#manual-rollback-on-render), then its public endpoints are checked again.

Initial public deployment verified on 16 November 2026.
Render service: schemaguard-2026.
Initial deployed commit: 9cf5694.
Rollback procedure documented; actual rollback
has not yet been demonstrated.

## Validation behavior

Create a uniquely named contract with at least one unique, nonempty required column name and a missing-value threshold from 0 to 100 percent. Upload a UTF-8 CSV up to 5 MiB. Header comparison is case-sensitive. Empty or whitespace-only cells count as missing. Missing required columns or a missing percentage above the threshold produce `FAIL` with every reason. Empty, malformed, non-UTF-8, headerless, inconsistent-width, and oversized files return an API error. The uploaded CSV is never altered or stored.

## Development workflow

Read the relevant GitHub Issue and its acceptance criteria before changing code. Follow [AGENTS.md](AGENTS.md), [architecture](docs/architecture.md), and [agent roles](docs/agent-roles.md). The Engineer implements and records actual verification; the QA Reviewer checks against the issue. Issue comments and closure require authorization.

This single-user slice has no authentication, incident response, automated recovery, or external AI service. The Render Free deployment described above is for a disposable demo because its SQLite database is ephemeral.
