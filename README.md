# OSINT Master

OSINT Master is an investigation platform for ingesting structured intelligence data and exploring relationships across entities in an interactive graph interface.

The platform is designed around the [FollowTheMoney](https://followthemoney.tech/) data model so investigations can align with the wider OpenAleph/Yente ecosystem, while using FalkorDB as the graph-native storage engine.

## Platform Description

OSINT Master enables investigators to:

- ingest FTM-compatible datasets into investigation workspaces,
- model people, companies, documents, assets, and relationships as a connected graph,
- explore links visually to corroborate information across multiple sources,
- inspect entity properties and relationship context during analysis,
- prepare for future integrations (including BYOK/proprietary data tooling).

The first release focuses on a strong foundation for graph-based investigation workflows, then expands into additional source connectors and extraction pipelines.

## Project Scope

### MVP Scope (current)

- Multi-investigation support (separate graph per investigation)
- FTM-first ingestion (`.ftm` / `.ijson` data)
- FastAPI backend for investigation/entity APIs
- FalkorDB-backed graph persistence and traversal
- React frontend with Cytoscape.js graph exploration
- Tailwind + shadcn/ui interface with light/dark theme toggle

### Planned Next Scope

- Structured extraction pipelines that produce FTM entities from documents
- Additional importers/connectors for new data sources and formats
- Stronger graph workflows (search, filters, advanced expansion)
- Optional BYOK integration paths for proprietary systems

### Out of Scope (for MVP)

- User authentication/authorization
- Full plugin marketplace/extension runtime
- Broad document ETL across many unstructured formats

## Tech Stack

- Frontend: Vite, React, React Router, Tailwind CSS, shadcn/ui, Cytoscape.js, Bun
- Backend: FastAPI, Pydantic
- Data model: FollowTheMoney
- Graph database: FalkorDB (self-hosted via Docker)

## Repository Layout

- `frontend/`: UI application and graph exploration interface
- `backend/`: API and ingestion services
- `scripts/`: utility scripts and sample data helpers
- `PLAN.md`: implementation roadmap and milestones

## Quick Start (Local Backend + Frontend)

1. Copy local environment defaults:

```bash
cp .env.example .env
```

2. Start infrastructure services (Docker only for dependencies):

```bash
docker compose up -d falkordb yente-index yente-app
```

3. Run backend on your host machine:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

4. Run frontend on your host machine:

```bash
cd frontend
bun install
bun run dev
```

The backend is available at `http://localhost:8000` and the frontend at `http://localhost:5173`.

## Documentation (MkDocs Material)

This repository now includes a MkDocs Material setup under `mkdocs.yml` and `docs/`.

Run docs locally from repository root:

```bash
uvx --from mkdocs mkdocs serve -a 127.0.0.1:8002
```

Build static docs site:

```bash
uvx --from mkdocs mkdocs build
```

## Notes

- FollowTheMoney support is currently optional in backend dependency groups (`uv sync --extra ftm`) due to local compiler requirements (`pyicu` build dependency).
- Detailed implementation plan and phases are documented in `PLAN.md`.
