from typing import List
from fastapi import APIRouter, HTTPException
from app.models import Domain, DomainCreate, DomainUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=Domain, status_code=201)
async def create_domain(domain: DomainCreate):
    db = get_db()
    domain_model = Domain(**domain.model_dump())
    entity_id = create_entity(db, "Domain", domain_model)
    created_entity = get_entity(db, "Domain", entity_id)
    return Domain(**created_entity)


@router.get("", response_model=List[Domain])
async def list_domains():
    db = get_db()
    entities = get_entities_by_label(db, "Domain")
    return [Domain(**e) for e in entities]


@router.get("/{domain_id}", response_model=Domain)
async def get_domain(domain_id: str):
    db = get_db()
    entity = get_entity(db, "Domain", domain_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Domain not found")
    return Domain(**entity)


@router.put("/{domain_id}", response_model=Domain)
async def update_domain(domain_id: str, domain_update: DomainUpdate):
    db = get_db()
    updates = domain_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Domain", domain_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Domain not found")
    return Domain(**entity)


@router.delete("/{domain_id}", status_code=204)
async def delete_domain(domain_id: str):
    db = get_db()
    deleted = delete_entity(db, "Domain", domain_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Domain not found")

