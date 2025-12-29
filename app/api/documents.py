from typing import List
from fastapi import APIRouter, HTTPException
from app.models import Document, DocumentCreate, DocumentUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=Document, status_code=201)
async def create_document(document: DocumentCreate):
    db = get_db()
    doc_model = Document(**document.model_dump())
    entity_id = create_entity(db, "Document", doc_model)
    created_entity = get_entity(db, "Document", entity_id)
    return Document(**created_entity)


@router.get("", response_model=List[Document])
async def list_documents():
    db = get_db()
    entities = get_entities_by_label(db, "Document")
    return [Document(**e) for e in entities]


@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str):
    db = get_db()
    entity = get_entity(db, "Document", document_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**entity)


@router.put("/{document_id}", response_model=Document)
async def update_document(document_id: str, document_update: DocumentUpdate):
    db = get_db()
    updates = document_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Document", document_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**entity)


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: str):
    db = get_db()
    deleted = delete_entity(db, "Document", document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

