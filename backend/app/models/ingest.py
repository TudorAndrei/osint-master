"""Ingestion response models."""

from pydantic import BaseModel


class IngestResult(BaseModel):
    """Response for ingestion operations."""

    processed: int
    nodes_created: int
    edges_created: int
    errors: list[str]
    status: str | None = None
    workflow_id: str | None = None
    message: str | None = None


class ExtractionStatus(BaseModel):
    """Status response for asynchronous extraction workflows."""

    workflow_id: str
    status: str
    result: dict | None = None
    error: str | None = None
