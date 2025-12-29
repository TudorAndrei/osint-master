"""Organizations API endpoints."""

from fastapi import APIRouter, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import Organization, OrganizationCreate, OrganizationUpdate

router = APIRouter()


@router.post("", status_code=201)
async def create_organization(organization: OrganizationCreate) -> Organization:
    """Create a new organization."""
    db = get_db()
    org_model = Organization(**organization.model_dump())
    entity_id = create_entity(db, "Organization", org_model)
    created_entity = get_entity(db, "Organization", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Organization(**created_entity)


@router.get("")
async def list_organizations() -> list[Organization]:
    """List all organizations."""
    db = get_db()
    entities = get_entities_by_label(db, "Organization")
    return [Organization(**e) for e in entities]


@router.get("/{organization_id}")
async def get_organization(organization_id: str) -> Organization:
    """Get an organization by ID."""
    db = get_db()
    entity = get_entity(db, "Organization", organization_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**entity)


@router.put("/{organization_id}")
async def update_organization(
    organization_id: str, organization_update: OrganizationUpdate,
) -> Organization:
    """Update an organization."""
    db = get_db()
    updates = organization_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Organization", organization_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**entity)


@router.delete("/{organization_id}", status_code=204)
async def delete_organization(organization_id: str) -> None:
    """Delete an organization."""
    db = get_db()
    deleted = delete_entity(db, "Organization", organization_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Organization not found")
