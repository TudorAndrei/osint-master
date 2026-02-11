"""Entity enrichment routes."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import EntityServiceDep, YenteServiceDep
from app.core.graph_service import GraphServiceError
from app.core.yente_service import YenteServiceError
from app.models.enrich import YenteLinkResponse, YenteSearchResponse

router = APIRouter()


def _sanitize_relation(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in name.upper())
    if not cleaned:
        return "YENTE_RELATED"
    if cleaned[0].isdigit():
        cleaned = f"R_{cleaned}"
    return f"YENTE_{cleaned}"


@router.get("/yente")
async def search_yente(
    service: YenteServiceDep,
    query: Annotated[str, Query(min_length=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> YenteSearchResponse:
    """Search Yente/OpenSanctions for entities."""
    try:
        return service.search(query, limit=limit)
    except YenteServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/yente/link/{investigation_id}/{entity_id}")
async def link_yente_entity(
    investigation_id: str,
    entity_id: str,
    yente: YenteServiceDep,
    entity_service: EntityServiceDep,
) -> YenteLinkResponse:
    """Link an entity to already-present graph entities using Yente adjacency."""
    try:
        linked_ids = yente.adjacent_entity_ids(entity_id)
        if not linked_ids:
            return YenteLinkResponse(
                investigation_id=investigation_id,
                entity_id=entity_id,
                linked_to=[],
                links_applied=0,
            )

        graph = entity_service.graph_service.create_investigation_graph(investigation_id)
        existing_rows = graph.query(
            "MATCH (n:Entity) WHERE n.id IN $ids RETURN n.id",
            params={"ids": linked_ids},
        ).result_set
        existing_ids = {str(row[0]) for row in existing_rows}
        if not existing_ids:
            return YenteLinkResponse(
                investigation_id=investigation_id,
                entity_id=entity_id,
                linked_to=[],
                links_applied=0,
            )

        relation = _sanitize_relation("adjacent")
        links_applied = 0
        for target_id in sorted(existing_ids):
            graph.query(
                "MATCH (a:Entity {id: $source}), (b:Entity {id: $target}) "
                f"MERGE (a)-[r:{relation}]->(b) "
                "SET r.schema = $schema "
                "SET r.source = 'yente' "
                "RETURN r",
                params={
                    "source": entity_id,
                    "target": target_id,
                    "schema": relation,
                },
            )
            links_applied += 1

        return YenteLinkResponse(
            investigation_id=investigation_id,
            entity_id=entity_id,
            linked_to=sorted(existing_ids),
            links_applied=links_applied,
        )
    except (YenteServiceError, GraphServiceError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
