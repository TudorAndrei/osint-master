# OSINT Master

OSINT (Open Source Intelligence) master project for collecting, analyzing, and managing intelligence from publicly available sources.

## Tech Stack

- Python 3.11+ (with uv for package management)
- FastAPI for REST API
- FalkorDB for graph database storage
- Pydantic for data validation
- Bun for tooling and scripts

## Setup

### Prerequisites

- Python 3.11+
- uv package manager
- FalkorDB (Redis-compatible graph database)

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Set up FalkorDB:
   - Install and run FalkorDB (or use Docker):
   ```bash
   docker run -d -p 6379:6379 falkordb/falkordb:latest
   ```

3. Configure environment (optional):
   Create a `.env` file:
   ```
   FALKORDB_HOST=localhost
   FALKORDB_PORT=6379
   FALKORDB_PASSWORD=
   GRAPH_NAME=osint
   ```

### Running the Application

Start the FastAPI server:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- `GET /health` - Check API and database status

### Entity Endpoints

All entities support CRUD operations:

- **Persons**: `/api/v1/persons`
- **Organizations**: `/api/v1/organizations`
- **Domains**: `/api/v1/domains`
- **IP Addresses**: `/api/v1/ip-addresses`
- **Email Addresses**: `/api/v1/email-addresses`
- **Social Media Profiles**: `/api/v1/social-media-profiles`
- **Documents**: `/api/v1/documents`
- **Findings**: `/api/v1/findings`
- **Sources**: `/api/v1/sources`

### Relationship Endpoints

- `POST /api/v1/relationships` - Create a relationship between entities
- `GET /api/v1/relationships?entity_id=<id>` - Get all relationships for an entity

## Entity Types

The system supports the following entity types, all defined with Pydantic models:

1. **Person** - Individual people with name, aliases, date of birth, nationality
2. **Organization** - Companies, groups, institutions
3. **Domain** - Domain names with registration details
4. **IPAddress** - IP addresses (IPv4/IPv6) with geolocation
5. **EmailAddress** - Email addresses with associated domains
6. **SocialMediaProfile** - Social media accounts with platform and username
7. **Document** - Files, articles, reports with metadata
8. **Finding** - Intelligence findings/reports with confidence levels
9. **Source** - Data sources with reliability ratings
10. **Relationship** - Connections between entities

## Project Structure

```
osint-master/
├── app/
│   ├── api/           # FastAPI route handlers
│   ├── db/            # Database connection and queries
│   ├── models/        # Pydantic models
│   └── main.py        # FastAPI application
├── openspec/          # OpenSpec specifications
└── pyproject.toml     # Python dependencies
```

## Development

This project uses OpenSpec for spec-driven development. See `openspec/AGENTS.md` for workflow details.

