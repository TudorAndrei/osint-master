"""Graph retrieval routes."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import GraphServiceDep
from app.core.graph_service import GraphServiceError
from app.models.graph import GraphPage

router = APIRouter()


@router.get("/{investigation_id}/graph")
async def get_graph(
    investigation_id: str,
    graph_service: GraphServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=2000)] = 500,
) -> GraphPage:
    """Fetch paginated graph nodes and edges for an investigation."""
    try:
        return graph_service.get_graph_page(investigation_id, skip=skip, limit=limit)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
