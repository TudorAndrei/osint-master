"""Email Addresses API endpoints."""

from fastapi import APIRouter, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import EmailAddress, EmailAddressCreate, EmailAddressUpdate

router = APIRouter()


@router.post("", status_code=201)
async def create_email_address(email_address: EmailAddressCreate) -> EmailAddress:
    """Create a new email address."""
    db = get_db()
    email_model = EmailAddress(**email_address.model_dump())
    entity_id = create_entity(db, "EmailAddress", email_model)
    created_entity = get_entity(db, "EmailAddress", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return EmailAddress(**created_entity)


@router.get("")
async def list_email_addresses() -> list[EmailAddress]:
    """List all email addresses."""
    db = get_db()
    entities = get_entities_by_label(db, "EmailAddress")
    return [EmailAddress(**e) for e in entities]


@router.get("/{email_address_id}")
async def get_email_address(email_address_id: str) -> EmailAddress:
    """Get an email address by ID."""
    db = get_db()
    entity = get_entity(db, "EmailAddress", email_address_id)
    if not entity:
        raise HTTPException(status_code=404, detail="EmailAddress not found")
    return EmailAddress(**entity)


@router.put("/{email_address_id}")
async def update_email_address(
    email_address_id: str, email_address_update: EmailAddressUpdate,
) -> EmailAddress:
    """Update an email address."""
    db = get_db()
    updates = email_address_update.model_dump(exclude_none=True)
    entity = update_entity(db, "EmailAddress", email_address_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="EmailAddress not found")
    return EmailAddress(**entity)


@router.delete("/{email_address_id}", status_code=204)
async def delete_email_address(email_address_id: str) -> None:
    """Delete an email address."""
    db = get_db()
    deleted = delete_entity(db, "EmailAddress", email_address_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="EmailAddress not found")
