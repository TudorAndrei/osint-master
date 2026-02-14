"""Notebook models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from datetime import datetime


def default_viewport() -> dict[str, float]:
    """Build an empty canvas viewport payload."""
    return {"x": 0.0, "y": 0.0, "zoom": 1.0}


class NotebookCanvas(BaseModel):
    """Investigation notebook canvas payload."""

    nodes: list[dict[str, Any]] = Field(default_factory=list)
    edges: list[dict[str, Any]] = Field(default_factory=list)
    viewport: dict[str, float] = Field(default_factory=default_viewport)


class NotebookDocument(BaseModel):
    """Notebook state returned to the client."""

    investigation_id: str
    version: int
    canvas_doc: NotebookCanvas
    created_at: datetime
    updated_at: datetime


class NotebookUpdate(BaseModel):
    """Notebook update request body."""

    version: int = Field(..., ge=1)
    canvas_doc: NotebookCanvas
