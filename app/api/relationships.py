from typing import List
from fastapi import APIRouter, HTTPException, Query
from app.models import Relationship, RelationshipCreate, RelationshipUpdate
from app.db import get_db, create_relationship, get_relationships

router = APIRouter()


@router.post("", response_model=Relationship, status_code=201)
async def create_relationship_endpoint(relationship: RelationshipCreate):
    db = get_db()
    props = relationship.model_dump(exclude={"source_entity_id", "target_entity_id", "relationship_type"})
    rel_id = create_relationship(
        db,
        relationship.source_entity_id,
        relationship.target_entity_id,
        relationship.relationship_type,
        props
    )
    rel_model = Relationship(
        id=rel_id,
        source_entity_id=relationship.source_entity_id,
        target_entity_id=relationship.target_entity_id,
        relationship_type=relationship.relationship_type,
        description=relationship.description,
        metadata=relationship.metadata
    )
    return rel_model


@router.get("", response_model=List[Relationship])
async def list_relationships(entity_id: str = Query(..., description="Entity ID to get relationships for")):
    db = get_db()
    relationships = get_relationships(db, entity_id)
    return [Relationship(**r) for r in relationships]

