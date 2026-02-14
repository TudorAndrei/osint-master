"""API dependencies for dependency injection."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.entity_service import EntityService
from app.core.extraction.workflow_service import ExtractionWorkflowService
from app.core.ftm_service import FTMService
from app.core.graph_service import GraphService
from app.core.ingest_service import IngestService
from app.core.investigation_service import InvestigationService
from app.core.notebook_service import NotebookService
from app.core.storage_service import StorageService
from app.core.yente_service import YenteService


@lru_cache
def get_graph_service() -> GraphService:
    """Get graph service singleton."""
    return GraphService()


@lru_cache
def get_ftm_service() -> FTMService:
    """Get FTM service singleton."""
    return FTMService()


@lru_cache
def get_investigation_service() -> InvestigationService:
    """Get investigation service singleton."""
    return InvestigationService(graph_service=get_graph_service())


@lru_cache
def get_entity_service() -> EntityService:
    """Get entity service singleton."""
    return EntityService(graph_service=get_graph_service(), ftm_service=get_ftm_service())


@lru_cache
def get_ingest_service() -> IngestService:
    """Get ingest service singleton."""
    return IngestService(entity_service=get_entity_service())


@lru_cache
def get_yente_service() -> YenteService:
    """Get Yente service singleton."""
    return YenteService()


@lru_cache
def get_storage_service() -> StorageService:
    """Get storage service singleton."""
    return StorageService()


@lru_cache
def get_extraction_workflow_service() -> ExtractionWorkflowService:
    """Get extraction workflow service singleton."""
    return ExtractionWorkflowService()


@lru_cache
def get_notebook_service() -> NotebookService:
    """Get notebook service singleton."""
    return NotebookService()


GraphServiceDep = Annotated[GraphService, Depends(get_graph_service)]
FTMServiceDep = Annotated[FTMService, Depends(get_ftm_service)]
InvestigationServiceDep = Annotated[InvestigationService, Depends(get_investigation_service)]
EntityServiceDep = Annotated[EntityService, Depends(get_entity_service)]
IngestServiceDep = Annotated[IngestService, Depends(get_ingest_service)]
YenteServiceDep = Annotated[YenteService, Depends(get_yente_service)]
StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]
ExtractionWorkflowServiceDep = Annotated[
    ExtractionWorkflowService,
    Depends(get_extraction_workflow_service),
]
NotebookServiceDep = Annotated[NotebookService, Depends(get_notebook_service)]
