"""Sources API endpoints."""

from fastapi import APIRouter, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import Source, SourceCreate, SourceUpdate

router = APIRouter()


@router.post("", status_code=201)
async def create_source(source: SourceCreate) -> Source:
    """Create a new source."""
    db = get_db()
    source_model = Source(**source.model_dump())
    entity_id = create_entity(db, "Source", source_model)
    created_entity = get_entity(db, "Source", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Source(**created_entity)


@router.get("")
async def list_sources() -> list[Source]:
    """List all sources."""
    db = get_db()
    entities = get_entities_by_label(db, "Source")
    return [Source(**e) for e in entities]


@router.get("/{source_id}")
async def get_source(source_id: str) -> Source:
    """Get a source by ID."""
    db = get_db()
    entity = get_entity(db, "Source", source_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Source not found")
    return Source(**entity)


@router.put("/{source_id}")
async def update_source(
    source_id: str, source_update: SourceUpdate,
) -> Source:
    """Update a source."""
    db = get_db()
    updates = source_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Source", source_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Source not found")
    return Source(**entity)


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: str) -> None:
    """Delete a source."""
    db = get_db()
    deleted = delete_entity(db, "Source", source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")
