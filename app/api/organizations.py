from typing import Annotated

from falkordb import Graph
from fastapi import APIRouter, Depends, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import Organization

router = APIRouter()


@router.post("", status_code=201)
async def create_organization(
    organization: Organization,
    db: Annotated[Graph, Depends(get_db)],
) -> Organization:
    org_model = Organization(**organization.model_dump())
    entity_id = create_entity(db, "Organization", org_model)
    created_entity = get_entity(db, "Organization", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Organization(**created_entity)


@router.get("")
async def list_organizations(
    db: Annotated[Graph, Depends(get_db)],
) -> list[Organization]:
    entities = get_entities_by_label(db, "Organization")
    return [Organization(**e) for e in entities]


@router.get("/{organization_id}")
async def get_organization(
    organization_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> Organization:
    entity = get_entity(db, "Organization", organization_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**entity)


@router.put("/{organization_id}")
async def update_organization(
    organization_id: str,
    organization_update: Organization,
    db: Annotated[Graph, Depends(get_db)],
) -> Organization:
    updates = organization_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Organization", organization_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**entity)


@router.delete("/{organization_id}", status_code=204)
async def delete_organization(
    organization_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> None:
    deleted = delete_entity(db, "Organization", organization_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Organization not found")
