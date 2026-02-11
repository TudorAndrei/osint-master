# OSINT Master - Implementation Plan

An investigation platform for corroborating information across multiple sources using FollowTheMoney (FTM) as the core data model.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Vite + React)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Graph Canvas   │  │  Entity Panel   │  │  File Uploader  │  │
│  │  (Cytoscape.js) │  │  (FTM Schema)   │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ REST API
┌───────────────────────────────▼─────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   API Routes    │  │  FTM Service    │  │  Ingest Engine  │  │
│  │  (entities,     │  │  (validation,   │  │  (file parsing, │  │
│  │   graph ops)    │  │   schema mgmt)  │  │   entity extract│  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐                                            │
│  │  Graph Service  │                                            │
│  │  (FalkorDB ops) │                                            │
│  └─────────────────┘                                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Cypher
┌───────────────────────────────▼─────────────────────────────────┐
│                      FalkorDB (Docker)                          │
│                   Graph: investigations                         │
│    Nodes: FTM Entities (Person, Company, Document, etc.)        │
│    Edges: FTM Relationships (Ownership, Directorship, etc.)     │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Database** | FalkorDB (Docker, self-hosted) |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2 |
| **FTM** | `followthemoney` library |
| **Frontend Runtime** | Bun |
| **Frontend Framework** | Vite, React 18, TypeScript |
| **Routing** | React Router v7 |
| **State** | TanStack Query (server state) |
| **Styling** | Tailwind CSS + shadcn/ui |
| **Theme** | Dark/Light mode with toggle |
| **Graph Viz** | Cytoscape.js |

## Data Model

### FTM to FalkorDB Mapping

FTM entities map to FalkorDB as follows:

- **Thing entities** (Person, Company, Document) → **Graph Nodes**
- **Interval entities** (Ownership, Directorship) → **Graph Edges**

```cypher
// Example: Person node
CREATE (n:Entity:Person:LegalEntity:Thing {
  id: "person-abc123",
  schema: "Person",
  _name: ["John Doe", "J. Doe"],
  _nationality: ["us"],
  _birthDate: ["1982-03-15"]
})

// Example: Ownership edge
MATCH (a {id: "person-abc123"}), (b {id: "company-def456"})
CREATE (a)-[r:OWNERSHIP {
  id: "ownership-xyz",
  schema: "Ownership",
  _percentage: ["51%"],
  _startDate: ["2020-01-01"]
}]->(b)
```

### Multi-Investigation Support

Each investigation is stored as a separate FalkorDB graph:
- `investigation_<uuid>` - Graph per investigation
- Metadata stored as graph properties or separate metadata node

## API Design

### Investigations
```
POST   /api/investigations              # Create new investigation
GET    /api/investigations              # List all investigations
GET    /api/investigations/{id}         # Get investigation details
DELETE /api/investigations/{id}         # Delete investigation + graph
```

### Entities (within investigation)
```
POST   /api/investigations/{id}/entities           # Create entity
GET    /api/investigations/{id}/entities           # List/search entities
GET    /api/investigations/{id}/entities/{eid}     # Get entity
PUT    /api/investigations/{id}/entities/{eid}     # Update entity
DELETE /api/investigations/{id}/entities/{eid}     # Delete entity
GET    /api/investigations/{id}/entities/{eid}/expand  # Get neighbors
```

### Ingestion
```
POST   /api/investigations/{id}/ingest             # Upload FTM JSON file
```

### Graph
```
GET    /api/investigations/{id}/graph              # Get full graph (paginated)
```

### Schema (global)
```
GET    /api/schema                                 # List all FTM schemata
GET    /api/schema/{name}                          # Get schema details
```

---

## Implementation Phases

### Phase 1: Backend Foundation

| Task | Status | Description |
|------|--------|-------------|
| 1.1 Backend project setup | ✅ | uv, FastAPI skeleton, config |
| 1.2 Docker Compose | ✅ | FalkorDB + persistence |
| 1.3 FalkorDB connection | ✅ | Connection service + health check |
| 1.4 FTM schema service | ✅ | Load schemata, expose via API |
| 1.5 Investigation CRUD | ✅ | Create/list/delete graphs |
| 1.6 Entity CRUD | ✅ | With FTM validation |
| 1.7 Entity expand | ✅ | Neighbors endpoint |

### Phase 2: Ingestion

| Task | Status | Description |
|------|--------|-------------|
| 2.1 FTM JSON ingestor | ✅ | Parse .ftm/.ijson files |
| 2.2 File upload endpoint | ✅ | With validation |

### Phase 3: Frontend

| Task | Status | Description |
|------|--------|-------------|
| 3.1 Frontend setup | ✅ | Bun, Vite, React, Tailwind, shadcn |
| 3.2 Dark/light theme | ✅ | With toggle |
| 3.3 API client | ✅ | TanStack Query setup |
| 3.4 Layout | ✅ | Header, sidebar, investigation list |
| 3.5 Graph canvas | ✅ | Cytoscape.js integration |
| 3.6 Entity panel | ✅ | View selected entity details |
| 3.7 Graph interactions | ✅ | Select, expand, pan/zoom |
| 3.8 File upload UI | ✅ | Drag & drop |

### Phase 4: Polish

| Task | Status | Description |
|------|--------|-------------|
| 4.1 Entity search/filter | ✅ | Search by name/property |
| 4.2 Schema-based styling | ✅ | Node icons/colors by type |
| 4.3 Graph layouts | ✅ | Force-directed, hierarchical |

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ with uv
- Bun (for frontend)

### Development Setup

1. **Start FalkorDB:**
   ```bash
   docker compose up -d falkordb
   ```

2. **Backend setup:**
   ```bash
   cd backend
   uv sync
   uv run uvicorn app.main:app --reload
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   bun install
   bun run dev
   ```

4. **Access:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - FalkorDB Browser: http://localhost:3000
   - API Docs: http://localhost:8000/docs

---

## Key Design Decisions

### 1. Entity ID Strategy
Support both FTM's content-hash IDs (`make_id()`) and explicit IDs for flexibility.

### 2. Relationship Modeling
Model FTM "Interval" entities as edges with properties for simple cases. Complex multi-entity relationships can use intermediate nodes if needed.

### 3. Schema Validation
Use the `followthemoney` Python library for validation on the backend. Frontend displays schema info but doesn't enforce.

### 4. Graph Rendering
Use Cytoscape.js with fcose (force-directed) layout as default. Schema-based styling for visual differentiation.

---

## Future Enhancements

- [ ] Structured output extraction (LLM-powered document parsing)
- [ ] CSV import with column mapping
- [ ] Yente integration for entity matching
- [ ] Yente data indexing workflow (bootstrap index and monitor ingestion status)
- [ ] Yente lookup adapter in backend (`/api/enrich/yente`) for search, retrieve, and match flows
- [ ] Entity enrichment pipeline: attach Yente/OpenSanctions matches to investigation entities
- [ ] Configure Yente manifests (`commercial.yml` vs custom datasets) per environment
- [ ] Add optional host volume mount for custom Yente datasets and local BYOD feeds
- [ ] Resolve API port strategy between FastAPI and Yente (e.g. `8000` vs `8001`)
- [ ] Add operational runbooks for Elasticsearch index health and Yente health checks
- [ ] OpenAleph data source connector
- [ ] Collaboration features (multi-user)
- [ ] Entity merging/deduplication
- [ ] Timeline visualization
- [ ] Export to various formats
