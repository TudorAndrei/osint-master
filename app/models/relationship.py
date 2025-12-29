from pydantic import BaseModel, Field, model_validator

from .base import BaseEntity


class Relationship(BaseEntity):
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(
        ...,
        min_length=1,
        description="Type of relationship",
    )
    description: str | None = Field(None, description="Relationship description")

    @model_validator(mode="after")
    def validate_not_self_referential(self):
        if self.source_entity_id == self.target_entity_id:
            msg = "Source and target entity IDs cannot be the same"
            raise ValueError(msg)
        return self

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "source_entity_id": "entity-1",
                "target_entity_id": "entity-2",
                "relationship_type": "OWNS",
                "description": "Person owns domain",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class RelationshipCreate(BaseModel):
    """Create model for Relationship entity."""

    source_entity_id: str
    target_entity_id: str
    relationship_type: str = Field(..., min_length=1)
    description: str | None = None
    metadata: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_not_self_referential(self):
        """Validate that source and target entity IDs are different."""
        if self.source_entity_id == self.target_entity_id:
            msg = "Source and target entity IDs cannot be the same"
            raise ValueError(msg)
        return self


class RelationshipUpdate(BaseModel):
    """Update model for Relationship entity."""

    source_entity_id: str | None = None
    target_entity_id: str | None = None
    relationship_type: str | None = Field(None, min_length=1)
    description: str | None = None
    metadata: dict | None = None
