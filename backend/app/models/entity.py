"""Entity models."""

from pydantic import BaseModel, Field


class EntityCreate(BaseModel):
    """Request model for creating an entity."""

    id: str | None = None  # Optional, will be generated if not provided
    schema_: str = Field(..., alias="schema")
    properties: dict[str, list[str]] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class EntityUpdate(BaseModel):
    """Request model for updating an entity."""

    properties: dict[str, list[str]]


class Entity(BaseModel):
    """Entity response model."""

    id: str
    schema_: str = Field(..., alias="schema")
    properties: dict[str, list[str]]

    model_config = {"populate_by_name": True}


class EntityExpand(BaseModel):
    """Response model for entity expansion (neighbors)."""

    entity: Entity
    neighbors: list[Entity]
    edges: list[dict]  # Edge information including relationship type


class DuplicateCandidate(BaseModel):
    """Potential duplicate pair for manual review."""

    left: Entity
    right: Entity
    similarity: float
    reason: str


class MergeEntitiesRequest(BaseModel):
    """Request model for manual merge operations."""

    source_ids: list[str]
    target_id: str
    merged_properties: dict[str, list[str]] | None = None


class MergeEntitiesResponse(BaseModel):
    """Response payload after merging entities."""

    target: Entity
    merged_source_ids: list[str]
