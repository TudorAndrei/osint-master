## OSINT Master Backend

FastAPI backend for the OSINT Master investigation platform.

### Development

```bash
uv sync
uv run uvicorn app.main:app --reload
```

The backend loads environment variables from `backend/.env` and `../.env`.
For local development with Docker-managed dependencies, run FalkorDB and Yente first:

```bash
docker compose up -d falkordb yente-index yente-app
```

### FollowTheMoney support

FTM is kept as an optional extra during initial scaffolding because `followthemoney`
pulls `pyicu`, which requires a C++ toolchain (`clang++`/`g++`) on the host.

Install it when you are ready to work on FTM-specific features:

```bash
uv sync --extra ftm
```
