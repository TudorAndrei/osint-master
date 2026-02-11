"""Yente enrichment request and response models."""

from pydantic import BaseModel, Field


class YenteSearchResult(BaseModel):
    """Normalized Yente search result."""

    id: str
    schema_: str = Field(..., alias="schema")
    caption: str
    score: float | None = None
    datasets: list[str] = Field(default_factory=list)
    properties: dict[str, list[str]] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class YenteSearchResponse(BaseModel):
    """Yente search response wrapper."""

    query: str
    total: int
    results: list[YenteSearchResult]


class YenteLinkResponse(BaseModel):
    """Response for linking an entity using Yente adjacency."""

    investigation_id: str
    entity_id: str
    linked_to: list[str]
    links_applied: int
