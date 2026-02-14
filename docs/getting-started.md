# Getting Started

## Prerequisites

- Docker + Docker Compose
- Python 3.12+
- `uv` for backend dependency management
- Bun for frontend development

## 1) Configure environment

```bash
cp .env.example .env
```

## 2) Start platform dependencies

```bash
docker compose up -d falkordb yente-index yente-app rustfs postgres
```

## 3) Run backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

The backend is served on `http://localhost:8000`.

## 4) Run frontend

```bash
cd frontend
bun install
bun run dev
```

The frontend is served on `http://localhost:5173`.

## 5) Run docs site (MkDocs Material)

From repository root:

```bash
uvx --from mkdocs mkdocs serve -a 127.0.0.1:8002
```

Documentation is then available at `http://127.0.0.1:8002`.

To build a static site:

```bash
uvx --from mkdocs mkdocs build
```

If you prefer a persistent local install, use `docs/requirements.txt` in your Python environment.
