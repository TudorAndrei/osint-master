from typing import List
from fastapi import APIRouter, HTTPException
from app.models import Source, SourceCreate, SourceUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=Source, status_code=201)
async def create_source(source: SourceCreate):
    db = get_db()
    source_model = Source(**source.model_dump())
    entity_id = create_entity(db, "Source", source_model)
    created_entity = get_entity(db, "Source", entity_id)
    return Source(**created_entity)


@router.get("", response_model=List[Source])
async def list_sources():
    db = get_db()
    entities = get_entities_by_label(db, "Source")
    return [Source(**e) for e in entities]


@router.get("/{source_id}", response_model=Source)
async def get_source(source_id: str):
    db = get_db()
    entity = get_entity(db, "Source", source_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Source not found")
    return Source(**entity)


@router.put("/{source_id}", response_model=Source)
async def update_source(source_id: str, source_update: SourceUpdate):
    db = get_db()
    updates = source_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Source", source_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Source not found")
    return Source(**entity)


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: str):
    db = get_db()
    deleted = delete_entity(db, "Source", source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found")

