"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from redis.exceptions import ConnectionError as RedisConnectionError
except ImportError:  # pragma: no cover - optional dependency
    RedisConnectionError = ConnectionError

from app.api.deps import get_graph_service
from app.api.routes import enrich, entities, graph, ingest, investigations, schema
from app.config import settings
from app.core.graph_service import GraphServiceError

app = FastAPI(
    title="OSINT Master",
    description="Investigation platform for corroborating information across multiple sources",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    status = "healthy"
    graph = "ok"

    try:
        graph_ok = get_graph_service().check_connection()
    except (GraphServiceError, RuntimeError, OSError, RedisConnectionError):
        graph_ok = False

    if not graph_ok:
        status = "degraded"
        graph = "unavailable"

    return {"status": status, "graph": graph}


app.include_router(investigations.router, prefix="/api/investigations", tags=["investigations"])
app.include_router(entities.router, prefix="/api/investigations", tags=["entities"])
app.include_router(ingest.router, prefix="/api/investigations", tags=["ingest"])
app.include_router(graph.router, prefix="/api/investigations", tags=["graph"])
app.include_router(schema.router, prefix="/api/schema", tags=["schema"])
app.include_router(enrich.router, prefix="/api/enrich", tags=["enrich"])
