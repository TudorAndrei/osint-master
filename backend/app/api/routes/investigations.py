"""Investigation CRUD routes."""

from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import InvestigationServiceDep
from app.core.graph_service import GraphServiceError
from app.models.investigation import Investigation, InvestigationCreate, InvestigationList

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    service: InvestigationServiceDep,
) -> Investigation:
    """Create a new investigation and backing graph."""
    try:
        return service.create(payload)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("")
async def list_investigations(service: InvestigationServiceDep) -> InvestigationList:
    """List all investigations."""
    try:
        return service.list()
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/{investigation_id}")
async def get_investigation(
    investigation_id: str,
    service: InvestigationServiceDep,
) -> Investigation:
    """Get details for one investigation."""
    try:
        investigation = service.get(investigation_id)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if investigation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")
    return investigation


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investigation(
    investigation_id: str,
    service: InvestigationServiceDep,
) -> Response:
    """Delete an investigation and its graph."""
    try:
        service.delete(investigation_id)
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
