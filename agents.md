# OSINT Master Agents

This file defines two implementation-focused agents for this repository.

## Project Software Stack

- **Runtime/Tooling**: Docker, Docker Compose, Git
- **Database/Graph**: FalkorDB (`falkordb/falkordb` container)
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, `uv`, optional `followthemoney`
- **Frontend**: Bun, Vite, React 18, TypeScript, React Router, TanStack Query
- **UI/Graph Rendering**: Tailwind CSS, shadcn/ui patterns, Cytoscape.js + `cytoscape-fcose`
- **Optional Intelligence Services**: Elasticsearch + Yente (OpenSanctions stack)

## Backend Agent

### Scope
- Owns everything under `backend/`.
- Implements API routes, services, models, ingestion, and FalkorDB integration.

### Stack
- Python 3.12+
- FastAPI + Pydantic v2
- `uv` for dependency and command execution
- FalkorDB as graph database
- Optional FollowTheMoney integration (`uv sync --extra ftm`)

### Primary Responsibilities
- Keep route contracts aligned with frontend types.
- Implement robust service-layer logic (not route-heavy logic).
- Validate FTM entities and normalize graph properties (`_name`, `_country`, etc.).
- Preserve investigation isolation (`investigation_<id>` graph strategy).
- Maintain stable health behavior (`/health`) and graceful degraded mode.

### Working Rules
- Add new behavior via `app/core/*_service.py` and thin route handlers.
- Keep models in `app/models/` and prefer explicit response models.
- Handle expected failures with `HTTPException` and meaningful status codes.
- Avoid destructive DB operations outside explicit delete endpoints.

### Validation Commands
- `cd backend && uv run python -m compileall app tests`
- `cd backend && uv run pytest`

### Done Criteria
- Endpoints return typed, consistent payloads.
- Tests pass and compile check passes.
- No regression in investigation/entity/graph/ingest routes.

---

## Frontend Agent

### Scope
- Owns everything under `frontend/`.
- Implements investigation UX, graph interactions, and API consumption.

### Stack
- Bun + Vite + React + TypeScript
- React Router
- TanStack Query
- Tailwind + shadcn/ui
- Cytoscape.js (+ fcose)

### Primary Responsibilities
- Keep UI in sync with backend API shapes in `src/api/types.ts`.
- Build investigation-first workflows:
  - create/list investigations
  - graph visualization
  - entity selection + expansion
  - ingestion upload flow
- Maintain responsive behavior for desktop and mobile widths.
- Keep visual consistency with current design tokens and theme support.

### Working Rules
- Use `apiClient` methods; avoid ad-hoc fetch calls in views.
- Keep route files focused on orchestration, not reusable UI primitives.
- Prefer strongly typed query/mutation data.
- Avoid introducing unused components or dead routes.

### Validation Commands
- `cd frontend && bun run lint`
- `cd frontend && bun run build`

### Done Criteria
- Build succeeds with no TypeScript errors.
- Lint passes.
- Core views (`home`, `investigation`) remain functional against running backend.
