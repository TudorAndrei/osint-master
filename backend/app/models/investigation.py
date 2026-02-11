"""Investigation models."""

from datetime import datetime

from pydantic import BaseModel, Field


class InvestigationCreate(BaseModel):
    """Request model for creating an investigation."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class Investigation(BaseModel):
    """Investigation response model."""

    id: str
    name: str
    description: str | None = None
    created_at: datetime
    entity_count: int = 0


class InvestigationList(BaseModel):
    """List of investigations response."""

    items: list[Investigation]
    total: int
