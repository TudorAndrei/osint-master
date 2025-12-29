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
from app.models import IPAddress

router = APIRouter()


@router.post("", status_code=201)
async def create_ip_address(
    ip_address: IPAddress,
    db: Annotated[Graph, Depends(get_db)],
) -> IPAddress:
    ip_model = IPAddress(**ip_address.model_dump())
    entity_id = create_entity(db, "IPAddress", ip_model)
    created_entity = get_entity(db, "IPAddress", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return IPAddress(**created_entity)


@router.get("")
async def list_ip_addresses(
    db: Annotated[Graph, Depends(get_db)],
) -> list[IPAddress]:
    entities = get_entities_by_label(db, "IPAddress")
    return [IPAddress(**e) for e in entities]


@router.get("/{ip_address_id}")
async def get_ip_address(
    ip_address_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> IPAddress:
    entity = get_entity(db, "IPAddress", ip_address_id)
    if not entity:
        raise HTTPException(status_code=404, detail="IPAddress not found")
    return IPAddress(**entity)


@router.put("/{ip_address_id}")
async def update_ip_address(
    ip_address_id: str,
    ip_address_update: IPAddress,
    db: Annotated[Graph, Depends(get_db)],
) -> IPAddress:
    updates = ip_address_update.model_dump(exclude_none=True)
    entity = update_entity(db, "IPAddress", ip_address_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="IPAddress not found")
    return IPAddress(**entity)


@router.delete("/{ip_address_id}", status_code=204)
async def delete_ip_address(
    ip_address_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> None:
    deleted = delete_entity(db, "IPAddress", ip_address_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="IPAddress not found")
