# Backend Agents

## Backend Implementation Agent

### Scope
- Entire `backend/` folder.
- FastAPI routes, core services, ingestion, and FalkorDB integration.

### Software Stack
- **Language**: Python 3.12+
- **API Framework**: FastAPI
- **Validation/Models**: Pydantic v2
- **Package/Task Runner**: `uv` (with `uv.lock`)
- **Graph Database**: FalkorDB (accessed via Python `falkordb` client)
- **Data Model**: FollowTheMoney (`followthemoney`, optional extra)
- **Testing**: `pytest`
- **Containerization**: `backend/Dockerfile` with `python:3.12-slim`

### Rules
- Keep route handlers thin; place business logic in `app/core/`.
- Use typed Pydantic request/response models from `app/models/`.
- Preserve investigation graph isolation (`investigation_<id>`).
- Keep health endpoint behavior stable (`/health` with graph status).
- Prefer explicit error handling with proper HTTP status codes.

### Validate Before Finishing
- `uv run python -m compileall app tests`
- `uv run pytest`

### Success Criteria
- API contracts stay consistent with frontend expectations.
- Tests pass and no syntax/type regressions are introduced.
