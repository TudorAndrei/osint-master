# Operations

## Core services

- **falkordb** (`6379`, `3000`) - graph database and browser UI.
- **backend** (`8000`) - FastAPI API service.
- **frontend** (`5174` in Docker compose) - web UI container.
- **yente-index** (`9200`) - Elasticsearch index.
- **yente-app** (`8001` mapped) - Yente API.
- **web-check** (`3002` mapped) - self-hosted website OSINT enrichment service.
- **rustfs** (`9000`, `9001`) - S3-compatible object storage.
- **postgres** (`5432`) - DBOS system database.

## Common health checks

- Backend: `GET http://localhost:8000/health`
- Yente: `GET http://localhost:8001/healthz`
- Web-Check: `GET http://localhost:3002/`
- Elasticsearch: `GET http://localhost:9200/_cluster/health`
- RustFS: `GET http://localhost:9000/`

## Environment variables

Platform defaults are defined in `.env.example`.

Key groups:

- Graph: `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_PASSWORD`
- API/Frontend: `API_HOST`, `API_PORT`, `VITE_API_URL`, `VITE_DEV_PROXY_TARGET`
- Auth: `CLERK_SECRET_KEY`, `VITE_CLERK_PUBLISHABLE_KEY`, `CLERK_AUTHORIZED_PARTIES`
- Enrichment: `OPENSANCTIONS_DELIVERY_TOKEN`, `YENTE_URL`, `YENTE_DATASET`
- Web enrichment: `WEBCHECK_ENABLED`, `WEBCHECK_BASE_URL`, `WEBCHECK_TIMEOUT_SECONDS`, `WEBCHECK_SUBSAMPLE_FIELDS`
- Infra enrichment: `SHODAN_ENABLED`, `SHODAN_API_KEY`, `SHODAN_MODE`
- Storage: `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET_NAME`
- Workflows: `DBOS_SYSTEM_DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

`SHODAN_MODE` supports:

- `platform` - backend uses a platform-managed `SHODAN_API_KEY`.
- `byok` - each user supplies their own Shodan key at request time.

## Troubleshooting quick guide

- If graph calls fail, confirm FalkorDB is healthy and reachable on port `6379`.
- If enrichment fails, verify Yente index and app containers are healthy.
- If document workflows fail, verify RustFS credentials and bucket configuration.
- If auth fails locally, verify Clerk public and secret keys in `.env`.
