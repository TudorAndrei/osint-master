"""Relationships API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.db import create_relationship, get_db, get_relationships
from app.models import Relationship, RelationshipCreate

router = APIRouter()


@router.post("", status_code=201)
async def create_relationship_endpoint(
    relationship: RelationshipCreate,
) -> Relationship:
    """Create a new relationship between entities."""
    db = get_db()
    props = relationship.model_dump(
        exclude={"source_entity_id", "target_entity_id", "relationship_type"},
    )
    rel_id = create_relationship(
        db,
        relationship.source_entity_id,
        relationship.target_entity_id,
        relationship.relationship_type,
        props,
    )
    return Relationship(
        id=rel_id,
        source_entity_id=relationship.source_entity_id,
        target_entity_id=relationship.target_entity_id,
        relationship_type=relationship.relationship_type,
        description=relationship.description,
        metadata=relationship.metadata,
    )


@router.get("")
async def list_relationships(
    entity_id: Annotated[str, Query(description="Entity ID to get relationships for")],
) -> list[Relationship]:
    """List all relationships for an entity."""
    db = get_db()
    relationships = get_relationships(db, entity_id)
    return [Relationship(**r) for r in relationships]
