"""Data ingestion routes."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.deps import ExtractionWorkflowServiceDep, IngestServiceDep, StorageServiceDep
from app.core.graph_service import GraphServiceError
from app.models.entity import EntityCreate
from app.models.ingest import ExtractionStatus, IngestResult

router = APIRouter()

FTM_EXTENSIONS = {".ftm", ".ijson", ".json", ".ndjson"}
UploadFileBody = Annotated[UploadFile, File(...)]


@router.post("/{investigation_id}/ingest")
async def ingest_file(
    investigation_id: str,
    ingest_service: IngestServiceDep,
    storage_service: StorageServiceDep,
    workflow_service: ExtractionWorkflowServiceDep,
    file: UploadFileBody,
) -> IngestResult:
    """Ingest structured FTM records or extract entities from uploaded documents."""
    try:
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        filename = file.filename or "upload.bin"
        extension = Path(filename).suffix.lower()

        if extension in FTM_EXTENSIONS:
            return ingest_service.ingest_file(
                investigation_id=investigation_id,
                filename=filename,
                content=content,
            )

        document = ingest_service.entity_service.create(
            investigation_id,
            EntityCreate(
                schema="Document",
                properties={
                    "fileName": [filename],
                    "mimeType": [file.content_type or "application/octet-stream"],
                    "extension": [extension],
                    "processingStatus": ["queued"],
                },
            ),
        )

        storage_key = storage_service.upload_bytes(
            investigation_id=investigation_id,
            document_id=document.id,
            filename=filename,
            content=content,
            content_type=file.content_type,
        )

        workflow_id = workflow_service.enqueue(
            investigation_id=investigation_id,
            document_id=document.id,
            storage_key=storage_key,
            filename=filename,
            content_type=file.content_type,
        )

        return IngestResult(
            processed=1,
            nodes_created=1,
            edges_created=0,
            errors=[],
            status="processing",
            workflow_id=workflow_id,
            message="Document uploaded and extraction workflow started",
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GraphServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/{investigation_id}/ingest/{workflow_id}/status")
async def get_extraction_status(
    investigation_id: str,
    workflow_id: str,
    workflow_service: ExtractionWorkflowServiceDep,
) -> ExtractionStatus:
    """Get extraction workflow status for a document ingestion request."""
    _ = investigation_id
    status_payload = workflow_service.get_status(workflow_id)
    return ExtractionStatus(**status_payload)
