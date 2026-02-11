"""Entity CRUD routes."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.deps import EntityServiceDep
from app.core.graph_service import GraphServiceError
from app.models.entity import (
    DuplicateCandidate,
    Entity,
    EntityCreate,
    EntityExpand,
    EntityUpdate,
    MergeEntitiesRequest,
    MergeEntitiesResponse,
)

router = APIRouter()


@router.post(
    "/{investigation_id}/entities",
    status_code=status.HTTP_201_CREATED,
)
async def create_entity(
    investigation_id: str,
    payload: EntityCreate,
    service: EntityServiceDep,
) -> Entity:
    """Create an entity in an investigation."""
    try:
        return service.create(investigation_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/{investigation_id}/entities")
async def list_entities(
    investigation_id: str,
    service: EntityServiceDep,
    search: Annotated[str | None, Query()] = None,
) -> list[Entity]:
    """List entities in an investigation."""
    try:
        return service.list(investigation_id, search=search)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/{investigation_id}/entities/{entity_id}")
async def get_entity(
    investigation_id: str,
    entity_id: str,
    service: EntityServiceDep,
) -> Entity:
    """Get a single entity by ID."""
    try:
        entity = service.get(investigation_id, entity_id)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return entity


@router.put("/{investigation_id}/entities/{entity_id}")
async def update_entity(
    investigation_id: str,
    entity_id: str,
    payload: EntityUpdate,
    service: EntityServiceDep,
) -> Entity:
    """Update an entity's properties."""
    try:
        entity = service.update(investigation_id, entity_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return entity


@router.delete("/{investigation_id}/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    investigation_id: str,
    entity_id: str,
    service: EntityServiceDep,
) -> Response:
    """Delete an entity by ID."""
    try:
        deleted = service.delete(investigation_id, entity_id)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{investigation_id}/entities/{entity_id}/expand")
async def expand_entity(
    investigation_id: str,
    entity_id: str,
    service: EntityServiceDep,
) -> EntityExpand:
    """Get neighboring entities and connecting edges."""
    try:
        expanded = service.expand(investigation_id, entity_id)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if expanded is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return expanded


@router.get("/{investigation_id}/entities/deduplicate/candidates")
async def find_duplicates(
    investigation_id: str,
    service: EntityServiceDep,
    schema: Annotated[str | None, Query()] = None,
    threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.7,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[DuplicateCandidate]:
    """Find potential duplicate entities for manual review."""
    try:
        return service.find_duplicates(
            investigation_id,
            schema=schema,
            threshold=threshold,
            limit=limit,
        )
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/{investigation_id}/entities/merge")
async def merge_entities(
    investigation_id: str,
    payload: MergeEntitiesRequest,
    service: EntityServiceDep,
) -> MergeEntitiesResponse:
    """Merge multiple entities into a selected target entity."""
    try:
        return service.merge_entities(
            investigation_id,
            source_ids=payload.source_ids,
            target_id=payload.target_id,
            merged_properties=payload.merged_properties,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
