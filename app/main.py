from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Response

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
from app.db.connection import close_connection_pool, init_connection_pool


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

api_router = APIRouter()

api_router.include_router(persons.router, prefix="/persons", tags=["persons"])
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["organizations"],
)
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(
    ip_addresses.router,
    prefix="/ip-addresses",
    tags=["ip-addresses"],
)
api_router.include_router(
    email_addresses.router,
    prefix="/email-addresses",
    tags=["email-addresses"],
)
api_router.include_router(
    social_media_profiles.router,
    prefix="/social-media-profiles",
    tags=["social-media-profiles"],
)
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(findings.router, prefix="/findings", tags=["findings"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(
    relationships.router,
    prefix="/relationships",
    tags=["relationships"],
)

app.include_router(api_router)


@app.get("/health", status_code=200)
async def health_check() -> Response:
    return Response(status_code=200)
