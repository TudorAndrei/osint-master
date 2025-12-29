from pydantic import BaseModel, Field

from .base import BaseEntity


class Finding(BaseEntity):
    title: str = Field(..., min_length=1, description="Finding title")
    description: str = Field(..., min_length=1, description="Finding description")
    confidence_level: str | None = Field(
        None, description="Confidence level (low/medium/high)",
    )
    related_entity_ids: list[str] = Field(
        default_factory=list, description="Related entity IDs",
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Suspicious Activity Detected",
                "description": "Multiple connections found between entities",
                "confidence_level": "high",
                "related_entity_ids": ["entity-1", "entity-2"],
                "tags": ["suspicious", "network"],
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class FindingCreate(BaseModel):
    """Create model for Finding entity."""

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    confidence_level: str | None = None
    related_entity_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class FindingUpdate(BaseModel):
    """Update model for Finding entity."""

    title: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    confidence_level: str | None = None
    related_entity_ids: list[str] | None = None
    tags: list[str] | None = None
    metadata: dict | None = None
