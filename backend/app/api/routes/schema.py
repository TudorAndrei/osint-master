"""FTM schema routes."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import FTMServiceDep
from app.models.schema import Schema, SchemaDetail

router = APIRouter()


@router.get("")
async def list_schemata(ftm_service: FTMServiceDep) -> list[Schema]:
    """List available FTM schemata."""
    return ftm_service.list_schemata()


@router.get("/{schema_name}")
async def get_schema(schema_name: str, ftm_service: FTMServiceDep) -> SchemaDetail:
    """Get one FTM schema by name."""
    schema = ftm_service.get_schema(schema_name)
    if schema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{schema_name}' not found",
        )
    return schema
