from typing import Annotated

from falkordb import Graph
from fastapi import APIRouter, Depends, Query

from app.db import create_relationship, get_db, get_relationships
from app.models import Relationship

router = APIRouter()


@router.post("", status_code=201)
async def create_relationship_endpoint(
    relationship: Relationship,
    db: Annotated[Graph, Depends(get_db)],
) -> Relationship:
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
    )


@router.get("")
async def list_relationships(
    entity_id: Annotated[str, Query(description="Entity ID to get relationships for")],
    db: Annotated[Graph, Depends(get_db)],
) -> list[Relationship]:
    relationships = get_relationships(db, entity_id)
    return [Relationship(**r) for r in relationships]
