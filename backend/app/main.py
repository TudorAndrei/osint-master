"""FastAPI application entry point."""

import logfire
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from redis.exceptions import ConnectionError as RedisConnectionError
except ImportError:  # pragma: no cover - optional dependency
    RedisConnectionError = ConnectionError

from app.api.auth import require_auth
from app.api.deps import get_graph_service
from app.api.routes import (
    auth,
    chat,
    enrich,
    entities,
    graph,
    ingest,
    investigations,
    notebook,
    schema,
)
from app.config import settings
from app.core.graph_service import GraphServiceError

app = FastAPI(
    title="OSINT Master",
    description="Investigation platform for corroborating information across multiple sources",
    version="0.1.0",
)
app.state.logfire_configured = False


def _configure_logfire() -> None:
    logfire_environment = settings.logfire_environment.strip() or (
        "development" if settings.debug else "production"
    )

    if settings.logfire_token:
        logfire.configure(
            service_name=settings.logfire_service_name,
            service_version="0.1.0",
            environment=logfire_environment,
            send_to_logfire=True,
            token=settings.logfire_token,
        )
    else:
        logfire.configure(
            service_name=settings.logfire_service_name,
            service_version="0.1.0",
            environment=logfire_environment,
            send_to_logfire=False,
        )

    logfire.instrument_httpx()
    logfire.instrument_pydantic()
    logfire.instrument_pydantic_ai()
    logfire.instrument_fastapi(app)


@app.on_event("startup")
async def startup_event() -> None:
    if app.state.logfire_configured:
        return
    _configure_logfire()
    app.state.logfire_configured = True


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


protected_dependencies = [Depends(require_auth)]

app.include_router(
    investigations.router,
    prefix="/api/investigations",
    tags=["investigations"],
    dependencies=protected_dependencies,
)
app.include_router(
    entities.router,
    prefix="/api/investigations",
    tags=["entities"],
    dependencies=protected_dependencies,
)
app.include_router(
    ingest.router,
    prefix="/api/investigations",
    tags=["ingest"],
    dependencies=protected_dependencies,
)
app.include_router(
    graph.router,
    prefix="/api/investigations",
    tags=["graph"],
    dependencies=protected_dependencies,
)
app.include_router(
    notebook.router,
    prefix="/api/investigations",
    tags=["notebook"],
    dependencies=protected_dependencies,
)
app.include_router(
    schema.router,
    prefix="/api/schema",
    tags=["schema"],
    dependencies=protected_dependencies,
)
app.include_router(
    enrich.router,
    prefix="/api/enrich",
    tags=["enrich"],
    dependencies=protected_dependencies,
)
app.include_router(
    chat.router,
    prefix="/api/chat",
    tags=["chat"],
    dependencies=protected_dependencies,
)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
