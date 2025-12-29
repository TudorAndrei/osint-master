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
from app.models import Document

router = APIRouter()


@router.post("", status_code=201)
async def create_document(
    document: Document,
    db: Annotated[Graph, Depends(get_db)],
) -> Document:
    doc_model = Document(**document.model_dump())
    entity_id = create_entity(db, "Document", doc_model)
    created_entity = get_entity(db, "Document", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Document(**created_entity)


@router.get("")
async def list_documents(
    db: Annotated[Graph, Depends(get_db)],
) -> list[Document]:
    entities = get_entities_by_label(db, "Document")
    return [Document(**e) for e in entities]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> Document:
    entity = get_entity(db, "Document", document_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**entity)


@router.put("/{document_id}")
async def update_document(
    document_id: str,
    document_update: Document,
    db: Annotated[Graph, Depends(get_db)],
) -> Document:
    updates = document_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Document", document_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**entity)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> None:
    deleted = delete_entity(db, "Document", document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
