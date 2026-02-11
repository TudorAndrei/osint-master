"""Investigation application service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from app.models.investigation import Investigation, InvestigationCreate, InvestigationList

if TYPE_CHECKING:
    from app.core.graph_service import GraphService


class InvestigationService:
    """Manage investigation metadata and graph lifecycle."""

    def __init__(self, graph_service: GraphService) -> None:
        self.graph_service = graph_service

    def _to_investigation(self, data: dict) -> Investigation:
        created_at = datetime.fromisoformat(data["created_at"])
        return Investigation(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            created_at=created_at,
            entity_count=self.graph_service.count_entities(data["id"]),
        )

    def create(self, payload: InvestigationCreate) -> Investigation:
        investigation_id = str(uuid4())
        self.graph_service.create_investigation_graph(investigation_id)
        self.graph_service.create_investigation_metadata(
            investigation_id=investigation_id,
            name=payload.name,
            description=payload.description,
        )
        data = self.graph_service.get_investigation_metadata(investigation_id)
        if data is None:
            data = {
                "id": investigation_id,
                "name": payload.name,
                "description": payload.description,
                "created_at": datetime.now(UTC).isoformat(),
            }
        return self._to_investigation(data)

    def list(self) -> InvestigationList:
        items = [
            self._to_investigation(row) for row in self.graph_service.list_investigation_metadata()
        ]
        return InvestigationList(items=items, total=len(items))

    def get(self, investigation_id: str) -> Investigation | None:
        data = self.graph_service.get_investigation_metadata(investigation_id)
        if data is None:
            return None
        return self._to_investigation(data)

    def delete(self, investigation_id: str) -> bool:
        exists = self.graph_service.get_investigation_metadata(investigation_id) is not None
        self.graph_service.delete_investigation_metadata(investigation_id)
        self.graph_service.delete_investigation(investigation_id)
        return exists
