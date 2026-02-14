# Backend API

The backend is a FastAPI service exposed by `backend/app/main.py`.

## Base endpoints

- `GET /health` - liveness and graph connectivity status.
- `GET /api/auth/me` - current authenticated principal context.

## Investigation endpoints

Prefix: `/api/investigations`

- `POST /` - create investigation
- `GET /` - list investigations
- `GET /{investigation_id}` - fetch investigation
- `DELETE /{investigation_id}` - delete investigation

## Entity and graph endpoints

Prefix: `/api/investigations`

- `POST /{investigation_id}/entities`
- `GET /{investigation_id}/entities`
- `GET /{investigation_id}/entities/{entity_id}`
- `PUT /{investigation_id}/entities/{entity_id}`
- `DELETE /{investigation_id}/entities/{entity_id}`
- `GET /{investigation_id}/entities/{entity_id}/expand`
- `GET /{investigation_id}/entities/deduplicate/candidates`
- `POST /{investigation_id}/entities/merge`
- `GET /{investigation_id}/graph`

## Ingestion endpoints

Prefix: `/api/investigations`

- `POST /{investigation_id}/ingest`
- `GET /{investigation_id}/ingest/{workflow_id}/status`

## Notebook endpoints

Prefix: `/api/investigations`

- `GET /{investigation_id}/notebook`
- `PUT /{investigation_id}/notebook`

## Schema, enrichment, and chat

- Prefix `/api/schema`
  - `GET /`
  - `GET /{schema_name}`
- Prefix `/api/enrich`
  - `GET /yente`
  - `POST /yente/link/{investigation_id}/{entity_id}`
- Prefix `/api/chat`
  - chat route module enabled in backend router registration

## Auth behavior

All investigation and data routes are mounted with `require_auth` dependency. The `/api/auth` route group is public and used to resolve session identity details.
