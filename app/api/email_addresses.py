from typing import List
from fastapi import APIRouter, HTTPException
from app.models import EmailAddress, EmailAddressCreate, EmailAddressUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=EmailAddress, status_code=201)
async def create_email_address(email_address: EmailAddressCreate):
    db = get_db()
    email_model = EmailAddress(**email_address.model_dump())
    entity_id = create_entity(db, "EmailAddress", email_model)
    created_entity = get_entity(db, "EmailAddress", entity_id)
    return EmailAddress(**created_entity)


@router.get("", response_model=List[EmailAddress])
async def list_email_addresses():
    db = get_db()
    entities = get_entities_by_label(db, "EmailAddress")
    return [EmailAddress(**e) for e in entities]


@router.get("/{email_address_id}", response_model=EmailAddress)
async def get_email_address(email_address_id: str):
    db = get_db()
    entity = get_entity(db, "EmailAddress", email_address_id)
    if not entity:
        raise HTTPException(status_code=404, detail="EmailAddress not found")
    return EmailAddress(**entity)


@router.put("/{email_address_id}", response_model=EmailAddress)
async def update_email_address(email_address_id: str, email_address_update: EmailAddressUpdate):
    db = get_db()
    updates = email_address_update.model_dump(exclude_none=True)
    entity = update_entity(db, "EmailAddress", email_address_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="EmailAddress not found")
    return EmailAddress(**entity)


@router.delete("/{email_address_id}", status_code=204)
async def delete_email_address(email_address_id: str):
    db = get_db()
    deleted = delete_entity(db, "EmailAddress", email_address_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="EmailAddress not found")

