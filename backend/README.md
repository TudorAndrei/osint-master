## OSINT Master Backend

FastAPI backend for the OSINT Master investigation platform.

### Development

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Install and run git hooks with prek:

```bash
uv run prek install
uv run prek run --all-files
```

The backend loads environment variables from `backend/.env` and `../.env`.
For local development with Docker-managed dependencies, run FalkorDB and Yente first:

```bash
docker compose up -d falkordb yente-index yente-app
```

### Logfire observability

Logfire instrumentation is enabled for FastAPI requests, HTTPX calls, Pydantic
validation, and Pydantic AI traces.

Set these environment variables to send telemetry to Logfire:

```bash
LOGFIRE_TOKEN=<your-logfire-write-token>
LOGFIRE_ENVIRONMENT=development
LOGFIRE_SERVICE_NAME=osint-master-backend
```

Notes:
- If `LOGFIRE_TOKEN` is present, telemetry is sent to Logfire.
- If `LOGFIRE_TOKEN` is missing, instrumentation remains enabled locally but no data is sent.
- Use `LOGFIRE_ENVIRONMENT=development` locally and `LOGFIRE_ENVIRONMENT=production` in prod.

### FollowTheMoney support

FTM is kept as an optional extra during initial scaffolding because `followthemoney`
pulls `pyicu`, which requires a C++ toolchain (`clang++`/`g++`) on the host.

Install it when you are ready to work on FTM-specific features:

```bash
uv sync --extra ftm
```
