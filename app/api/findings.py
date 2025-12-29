"""Findings API endpoints."""

from fastapi import APIRouter, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import Finding, FindingCreate, FindingUpdate

router = APIRouter()


@router.post("", status_code=201)
async def create_finding(finding: FindingCreate) -> Finding:
    """Create a new finding."""
    db = get_db()
    finding_model = Finding(**finding.model_dump())
    entity_id = create_entity(db, "Finding", finding_model)
    created_entity = get_entity(db, "Finding", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Finding(**created_entity)


@router.get("")
async def list_findings() -> list[Finding]:
    """List all findings."""
    db = get_db()
    entities = get_entities_by_label(db, "Finding")
    return [Finding(**e) for e in entities]


@router.get("/{finding_id}")
async def get_finding(finding_id: str) -> Finding:
    """Get a finding by ID."""
    db = get_db()
    entity = get_entity(db, "Finding", finding_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Finding not found")
    return Finding(**entity)


@router.put("/{finding_id}")
async def update_finding(
    finding_id: str, finding_update: FindingUpdate,
) -> Finding:
    """Update a finding."""
    db = get_db()
    updates = finding_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Finding", finding_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Finding not found")
    return Finding(**entity)


@router.delete("/{finding_id}", status_code=204)
async def delete_finding(finding_id: str) -> None:
    """Delete a finding."""
    db = get_db()
    deleted = delete_entity(db, "Finding", finding_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Finding not found")
