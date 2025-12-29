from datetime import datetime

from pydantic import Field

from .base import EntityMixin


class Source(EntityMixin):
    source_name: str = Field(..., min_length=1, description="Source name")
    source_type: str | None = Field(None, description="Source type")
    url: str | None = Field(None, description="Source URL")
    collection_date: datetime | None = Field(
        None,
        description="Date when data was collected",
    )
    reliability: str | None = Field(None, description="Source reliability rating")
    description: str | None = Field(None, description="Additional description")
