"""Investigation notebook routes."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import NotebookServiceDep
from app.core.notebook_service import NotebookConflictError
from app.models.notebook import NotebookDocument, NotebookUpdate

router = APIRouter()


@router.get("/{investigation_id}/notebook")
async def get_notebook(
    investigation_id: str,
    service: NotebookServiceDep,
) -> NotebookDocument:
    """Get or create the notebook associated with an investigation."""
    try:
        return service.get_or_create(investigation_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.put("/{investigation_id}/notebook")
async def update_notebook(
    investigation_id: str,
    payload: NotebookUpdate,
    service: NotebookServiceDep,
) -> NotebookDocument:
    """Persist the notebook using optimistic version checks."""
    try:
        return service.save(
            investigation_id=investigation_id,
            version=payload.version,
            canvas_doc=payload.canvas_doc,
        )
    except NotebookConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
