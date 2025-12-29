from typing import List
from fastapi import APIRouter, HTTPException
from app.models import Finding, FindingCreate, FindingUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=Finding, status_code=201)
async def create_finding(finding: FindingCreate):
    db = get_db()
    finding_model = Finding(**finding.model_dump())
    entity_id = create_entity(db, "Finding", finding_model)
    created_entity = get_entity(db, "Finding", entity_id)
    return Finding(**created_entity)


@router.get("", response_model=List[Finding])
async def list_findings():
    db = get_db()
    entities = get_entities_by_label(db, "Finding")
    return [Finding(**e) for e in entities]


@router.get("/{finding_id}", response_model=Finding)
async def get_finding(finding_id: str):
    db = get_db()
    entity = get_entity(db, "Finding", finding_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Finding not found")
    return Finding(**entity)


@router.put("/{finding_id}", response_model=Finding)
async def update_finding(finding_id: str, finding_update: FindingUpdate):
    db = get_db()
    updates = finding_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Finding", finding_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Finding not found")
    return Finding(**entity)


@router.delete("/{finding_id}", status_code=204)
async def delete_finding(finding_id: str):
    db = get_db()
    deleted = delete_entity(db, "Finding", finding_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Finding not found")

