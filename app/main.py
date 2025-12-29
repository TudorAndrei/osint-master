from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.connection import get_db, close_db
from app.api import (
    persons,
    organizations,
    domains,
    ip_addresses,
    email_addresses,
    social_media_profiles,
    documents,
    findings,
    sources,
    relationships,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_db()
    yield
    close_db()


app = FastAPI(
    title="OSINT Master API",
    description="API for managing OSINT findings and entities",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(domains.router, prefix="/api/v1/domains", tags=["domains"])
app.include_router(ip_addresses.router, prefix="/api/v1/ip-addresses", tags=["ip-addresses"])
app.include_router(email_addresses.router, prefix="/api/v1/email-addresses", tags=["email-addresses"])
app.include_router(social_media_profiles.router, prefix="/api/v1/social-media-profiles", tags=["social-media-profiles"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(findings.router, prefix="/api/v1/findings", tags=["findings"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])
app.include_router(relationships.router, prefix="/api/v1/relationships", tags=["relationships"])


@app.get("/health")
async def health_check():
    try:
        db = get_db()
        db.query("RETURN 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

