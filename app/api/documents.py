"""Documents API endpoints."""

from fastapi import APIRouter, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import Document, DocumentCreate, DocumentUpdate

router = APIRouter()


@router.post("", status_code=201)
async def create_document(document: DocumentCreate) -> Document:
    """Create a new document."""
    db = get_db()
    doc_model = Document(**document.model_dump())
    entity_id = create_entity(db, "Document", doc_model)
    created_entity = get_entity(db, "Document", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Document(**created_entity)


@router.get("")
async def list_documents() -> list[Document]:
    """List all documents."""
    db = get_db()
    entities = get_entities_by_label(db, "Document")
    return [Document(**e) for e in entities]


@router.get("/{document_id}")
async def get_document(document_id: str) -> Document:
    """Get a document by ID."""
    db = get_db()
    entity = get_entity(db, "Document", document_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**entity)


@router.put("/{document_id}")
async def update_document(
    document_id: str, document_update: DocumentUpdate,
) -> Document:
    """Update a document."""
    db = get_db()
    updates = document_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Document", document_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**entity)


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: str) -> None:
    """Delete a document."""
    db = get_db()
    deleted = delete_entity(db, "Document", document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
