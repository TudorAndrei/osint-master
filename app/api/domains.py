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
from app.models import Domain

router = APIRouter()


@router.post("", status_code=201)
async def create_domain(
    domain: Domain,
    db: Annotated[Graph, Depends(get_db)],
) -> Domain:
    domain_model = Domain(**domain.model_dump())
    entity_id = create_entity(db, "Domain", domain_model)
    created_entity = get_entity(db, "Domain", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Domain(**created_entity)


@router.get("")
async def list_domains(
    db: Annotated[Graph, Depends(get_db)],
) -> list[Domain]:
    entities = get_entities_by_label(db, "Domain")
    return [Domain(**e) for e in entities]


@router.get("/{domain_id}")
async def get_domain(
    domain_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> Domain:
    entity = get_entity(db, "Domain", domain_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Domain not found")
    return Domain(**entity)


@router.put("/{domain_id}")
async def update_domain(
    domain_id: str,
    domain_update: Domain,
    db: Annotated[Graph, Depends(get_db)],
) -> Domain:
    updates = domain_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Domain", domain_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Domain not found")
    return Domain(**entity)


@router.delete("/{domain_id}", status_code=204)
async def delete_domain(
    domain_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> None:
    deleted = delete_entity(db, "Domain", domain_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Domain not found")
