"""Graph query and response models."""

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Node in graph response."""

    id: str
    schema_: str = Field(..., alias="schema")
    label: str  # Display label (usually first name value)
    properties: dict[str, list[str]]

    model_config = {"populate_by_name": True}


class GraphEdge(BaseModel):
    """Edge in graph response."""

    id: str
    source: str  # Source node ID
    target: str  # Target node ID
    schema_: str = Field(..., alias="schema")  # Relationship type (e.g., "Ownership")
    label: str  # Display label
    properties: dict[str, list[str]]

    model_config = {"populate_by_name": True}


class GraphData(BaseModel):
    """Full graph data response."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]


class GraphPage(BaseModel):
    """Paginated graph data response."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]
    total_nodes: int
    total_edges: int


class GraphQuery(BaseModel):
    """Custom graph query request."""

    cypher: str  # Raw Cypher query (for advanced users)
