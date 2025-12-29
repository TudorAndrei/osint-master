from typing import List
from fastapi import APIRouter, HTTPException
from app.models import Organization, OrganizationCreate, OrganizationUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=Organization, status_code=201)
async def create_organization(organization: OrganizationCreate):
    db = get_db()
    org_model = Organization(**organization.model_dump())
    entity_id = create_entity(db, "Organization", org_model)
    created_entity = get_entity(db, "Organization", entity_id)
    return Organization(**created_entity)


@router.get("", response_model=List[Organization])
async def list_organizations():
    db = get_db()
    entities = get_entities_by_label(db, "Organization")
    return [Organization(**e) for e in entities]


@router.get("/{organization_id}", response_model=Organization)
async def get_organization(organization_id: str):
    db = get_db()
    entity = get_entity(db, "Organization", organization_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**entity)


@router.put("/{organization_id}", response_model=Organization)
async def update_organization(organization_id: str, organization_update: OrganizationUpdate):
    db = get_db()
    updates = organization_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Organization", organization_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**entity)


@router.delete("/{organization_id}", status_code=204)
async def delete_organization(organization_id: str):
    db = get_db()
    deleted = delete_entity(db, "Organization", organization_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Organization not found")

