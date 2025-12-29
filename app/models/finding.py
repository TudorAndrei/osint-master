from pydantic import Field

from .base import EntityMixin


class Finding(EntityMixin):
    title: str = Field(..., min_length=1, description="Finding title")
    description: str = Field(..., min_length=1, description="Finding description")
    confidence_level: str | None = Field(
        None,
        description="Confidence level (low/medium/high)",
    )
    related_entity_ids: list[str] = Field(
        default_factory=list,
        description="Related entity IDs",
    )
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
