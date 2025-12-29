from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from falkordb import Graph  # pyright: ignore[reportMissingTypeStubs]
from fastapi import Depends, FastAPI

from app.api import (
    documents,
    domains,
    email_addresses,
    findings,
    ip_addresses,
    organizations,
    persons,
    relationships,
    social_media_profiles,
    sources,
)
from app.db.connection import close_connection_pool, get_db, init_connection_pool


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    init_connection_pool()
    yield
    close_connection_pool()


app = FastAPI(
    title="OSINT Master API",
    description="API for managing OSINT findings and entities",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(
    organizations.router,
    prefix="/api/v1/organizations",
    tags=["organizations"],
)
app.include_router(domains.router, prefix="/api/v1/domains", tags=["domains"])
app.include_router(
    ip_addresses.router,
    prefix="/api/v1/ip-addresses",
    tags=["ip-addresses"],
)
app.include_router(
    email_addresses.router,
    prefix="/api/v1/email-addresses",
    tags=["email-addresses"],
)
app.include_router(
    social_media_profiles.router,
    prefix="/api/v1/social-media-profiles",
    tags=["social-media-profiles"],
)
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(findings.router, prefix="/api/v1/findings", tags=["findings"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])
app.include_router(
    relationships.router,
    prefix="/api/v1/relationships",
    tags=["relationships"],
)


@app.get("/health")
async def health_check(
    db: Annotated[Graph, Depends(get_db)],
) -> dict[str, str]:
    try:
        _ = db.query("RETURN 1")
    except (ConnectionError, RuntimeError, ValueError) as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
    else:
        return {"status": "healthy", "database": "connected"}
