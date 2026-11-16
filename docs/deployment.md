# Deployment and rollback

## Render Docker web service

1. Push the repository to GitHub. In the [Render Dashboard](https://dashboard.render.com/), choose **New > Web Service**, connect the GitHub account, and select `devPaulX/schema-guard-zoomcamp-2026` as a connected repository. A service created from a public Git URL or prebuilt image does not support GitHub-connected auto-deploys.
2. Choose branch `main`, runtime **Docker**, and the repository-root `Dockerfile`. Select a plan (Free is sufficient for a disposable demo), then create the service. The image starts Uvicorn on `0.0.0.0:8000`; no separate start command or secrets are needed.
3. In the service **Settings**, set **Health Check Path** to `/api/health`. Wait until the initial deploy is live and the health check passes.
4. In **Settings > Auto-Deploy**, select **After CI Checks Pass**. The default **On Commit** setting does not gate deployment on CI. The `CI / test-and-build` GitHub Actions check runs on pushes to `main` and pull requests targeting `main`; it runs all tests, including Chromium, before building the Docker image. A failed test or image build makes the check fail, so Render does not deploy that commit. Confirm the check appears on a pushed commit and that Render shows **After CI Checks Pass**. Render treats GitHub check conclusions `success`, `neutral`, and `skipped` as passing, so keep this workflow enabled and do not add skip conditions. For merge protection, also require `CI / test-and-build` in GitHub's `main` branch protection rules.

The Render service builds its own Docker image from the connected Git commit; the CI image is only a build check and is not pushed to a registry. No deploy token or GitHub write permission is required. A GitHub Actions run is only available after this workflow is pushed, so local verification alone does not prove the gate is active.

### Verify the public endpoint

Use the service's actual URL from the Render Dashboard. Replace `YOUR-SERVICE` below with its service name:

```sh
curl --fail-with-body https://YOUR-SERVICE.onrender.com/api/health
curl --fail-with-body https://YOUR-SERVICE.onrender.com/
```

Expect HTTP 200, `{"status":"ok"}` from `/api/health`, and the SchemaGuard dashboard at `/`. From the public dashboard, create a disposable contract, validate a small UTF-8 CSV, and confirm the result appears in history. Check that the Render **Deploys** page identifies the expected Git commit. Record the URL, commit, CI run, and observed responses as deployment evidence only after doing these checks. This repository does not include evidence of a live Render deployment.

### Manual rollback on Render

1. In the Render Dashboard, open the SchemaGuard web service's **Deploys** page. Identify a previous **successful** deploy and its commit. Recent build artifacts must still be retained for Render's rollback button to be available.
2. Click **Rollback** on that deploy, then click **Rollback to this deploy** on the confirmation page. Wait for the rollback deploy to become live.
3. Recheck `https://YOUR-SERVICE.onrender.com/api/health` and `/`, and verify the active deploy/commit on the **Deploys** page. Record the rollback deploy and public responses if collecting Issue #4 evidence.
4. Dashboard rollback disables auto-deploys. After fixing and testing the faulty version, return to **Settings > Auto-Deploy** and select **After CI Checks Pass** again before resuming automatic deployment.

Rollback restores an earlier application build, not SQLite data. It cannot recover lost contracts or history. [Render's rollback guide](https://render.com/docs/rollbacks) describes artifact retention and the exact dashboard flow.

### SQLite on Render Free

The application writes SQLite to `/app/data/schemaguard.db`. Render's default filesystem is ephemeral: deploys, restarts, and instance replacement can erase the database. Render Free web services cannot use persistent disks. Therefore the Free deployment is a disposable demonstration; do not rely on it for durable contracts or validation history. A code rollback does not restore that database. A persistent Render disk requires a paid service, and a durable production data design is outside this issue. The app has no authentication, so do not put sensitive data in a public demo.

## Persistent local Docker deployment

From the repository root, with Docker running, use the existing Compose file. It mounts the named `schemaguard_data` volume at `/app/data`, where SQLite writes `schemaguard.db`:

```sh
docker compose up --build -d
docker compose ps
curl --fail-with-body http://127.0.0.1:8000/api/health
```

Create a contract and validation from the local dashboard at <http://127.0.0.1:8000/>, then restart and confirm they are still listed:

```sh
docker compose restart
curl --fail-with-body http://127.0.0.1:8000/api/contracts
curl --fail-with-body http://127.0.0.1:8000/api/validations
docker compose down
docker compose up -d
```

The volume persists across these commands and image rebuilds. `docker compose down --volumes` deletes it, including the SQLite database. The local `data/schemaguard.db` file and the Compose volume are separate stores.
