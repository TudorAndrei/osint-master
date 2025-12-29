from datetime import datetime

from pydantic import BaseModel, Field

from .base import BaseEntity


class Source(BaseEntity):
    source_name: str = Field(..., min_length=1, description="Source name")
    source_type: str | None = Field(None, description="Source type")
    url: str | None = Field(None, description="Source URL")
    collection_date: datetime | None = Field(
        None, description="Date when data was collected",
    )
    reliability: str | None = Field(None, description="Source reliability rating")
    description: str | None = Field(None, description="Additional description")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "source_name": "Public Database",
                "source_type": "Database",
                "url": "https://example.com/database",
                "collection_date": "2024-01-01T00:00:00",
                "reliability": "high",
                "description": "Public records database",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class SourceCreate(BaseModel):
    """Create model for Source entity."""

    source_name: str = Field(..., min_length=1)
    source_type: str | None = None
    url: str | None = None
    collection_date: datetime | None = None
    reliability: str | None = None
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class SourceUpdate(BaseModel):
    """Update model for Source entity."""

    source_name: str | None = Field(None, min_length=1)
    source_type: str | None = None
    url: str | None = None
    collection_date: datetime | None = None
    reliability: str | None = None
    description: str | None = None
    metadata: dict | None = None
