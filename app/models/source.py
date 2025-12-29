from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseEntity


class Source(BaseEntity):
    source_name: str = Field(..., min_length=1, description="Source name")
    source_type: Optional[str] = Field(None, description="Source type")
    url: Optional[str] = Field(None, description="Source URL")
    collection_date: Optional[datetime] = Field(None, description="Date when data was collected")
    reliability: Optional[str] = Field(None, description="Source reliability rating")
    description: Optional[str] = Field(None, description="Additional description")

    class Config:
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
                "metadata": {}
            }
        }


class SourceCreate(BaseModel):
    source_name: str = Field(..., min_length=1)
    source_type: Optional[str] = None
    url: Optional[str] = None
    collection_date: Optional[datetime] = None
    reliability: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class SourceUpdate(BaseModel):
    source_name: Optional[str] = Field(None, min_length=1)
    source_type: Optional[str] = None
    url: Optional[str] = None
    collection_date: Optional[datetime] = None
    reliability: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

