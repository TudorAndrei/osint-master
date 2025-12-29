from typing import List
from fastapi import APIRouter, HTTPException
from app.models import IPAddress, IPAddressCreate, IPAddressUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=IPAddress, status_code=201)
async def create_ip_address(ip_address: IPAddressCreate):
    db = get_db()
    ip_model = IPAddress(**ip_address.model_dump())
    entity_id = create_entity(db, "IPAddress", ip_model)
    created_entity = get_entity(db, "IPAddress", entity_id)
    return IPAddress(**created_entity)


@router.get("", response_model=List[IPAddress])
async def list_ip_addresses():
    db = get_db()
    entities = get_entities_by_label(db, "IPAddress")
    return [IPAddress(**e) for e in entities]


@router.get("/{ip_address_id}", response_model=IPAddress)
async def get_ip_address(ip_address_id: str):
    db = get_db()
    entity = get_entity(db, "IPAddress", ip_address_id)
    if not entity:
        raise HTTPException(status_code=404, detail="IPAddress not found")
    return IPAddress(**entity)


@router.put("/{ip_address_id}", response_model=IPAddress)
async def update_ip_address(ip_address_id: str, ip_address_update: IPAddressUpdate):
    db = get_db()
    updates = ip_address_update.model_dump(exclude_none=True)
    entity = update_entity(db, "IPAddress", ip_address_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="IPAddress not found")
    return IPAddress(**entity)


@router.delete("/{ip_address_id}", status_code=204)
async def delete_ip_address(ip_address_id: str):
    db = get_db()
    deleted = delete_entity(db, "IPAddress", ip_address_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="IPAddress not found")

