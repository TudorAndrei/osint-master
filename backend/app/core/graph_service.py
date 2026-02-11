"""FalkorDB graph operations service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol, cast

try:
    from falkordb import FalkorDB  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    FalkorDB = None

from app.config import settings
from app.models.graph import GraphEdge, GraphNode, GraphPage


class GraphServiceError(RuntimeError):
    """Raised when graph operations fail."""


class GraphHandle(Protocol):
    def query(self, query: str, params: object = None) -> object: ...

    def delete(self) -> None: ...


class DbHandle(Protocol):
    def select_graph(self, graph_id: str) -> GraphHandle: ...

    def list_graphs(self) -> list[str]: ...


class GraphService:
    """Service for FalkorDB graph operations."""

    INVESTIGATION_PREFIX = "investigation_"
    META_GRAPH = "investigations_meta"

    def __init__(self) -> None:
        self.db: object | None = None
        self._init_error: str | None = None
        if FalkorDB is None:
            self._init_error = "falkordb package is not installed. Run `uv sync` in backend/."
            return

        self.db = FalkorDB(
            host=settings.falkordb_host,
            port=settings.falkordb_port,
            password=settings.falkordb_password,
        )

    def _require_db(self) -> DbHandle:
        if self.db is None:
            raise GraphServiceError(self._init_error or "FalkorDB client is unavailable")
        return cast("DbHandle", self.db)

    def graph_name(self, investigation_id: str) -> str:
        """Build a graph name from investigation ID."""
        return f"{self.INVESTIGATION_PREFIX}{investigation_id}"

    def create_investigation_graph(self, investigation_id: str) -> GraphHandle:
        """Create (or fetch) an investigation graph."""
        return self._require_db().select_graph(self.graph_name(investigation_id))

    def _meta_graph(self) -> GraphHandle:
        return self._require_db().select_graph(self.META_GRAPH)

    def create_investigation_metadata(
        self,
        investigation_id: str,
        name: str,
        description: str | None,
    ) -> None:
        """Persist investigation metadata in a dedicated graph."""
        graph = self._meta_graph()
        created_at = datetime.now(UTC).isoformat()
        graph.query(
            "MERGE (i:Investigation {id: $id}) "
            "SET i.name = $name, i.description = $description, i.created_at = $created_at",
            params={
                "id": investigation_id,
                "name": name,
                "description": description,
                "created_at": created_at,
            },
        )

    def list_investigation_metadata(self) -> list[dict[str, Any]]:
        """Return all stored investigation metadata."""
        graph = self._meta_graph()
        result = graph.query(
            "MATCH (i:Investigation) "
            "RETURN i.id, i.name, i.description, i.created_at "
            "ORDER BY i.created_at DESC",
        ).result_set

        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
            }
            for row in result
        ]

    def get_investigation_metadata(self, investigation_id: str) -> dict[str, Any] | None:
        """Get one investigation metadata item."""
        graph = self._meta_graph()
        result = graph.query(
            "MATCH (i:Investigation {id: $id}) "
            "RETURN i.id, i.name, i.description, i.created_at LIMIT 1",
            params={"id": investigation_id},
        ).result_set
        if not result:
            return None
        row = result[0]
        return {"id": row[0], "name": row[1], "description": row[2], "created_at": row[3]}

    def delete_investigation_metadata(self, investigation_id: str) -> None:
        """Delete one investigation metadata item."""
        graph = self._meta_graph()
        graph.query(
            "MATCH (i:Investigation {id: $id}) DETACH DELETE i",
            params={"id": investigation_id},
        )

    def list_investigations(self) -> list[str]:
        """List investigation IDs discovered from graph names."""
        graphs = self._require_db().list_graphs()
        return [
            name.replace(self.INVESTIGATION_PREFIX, "", 1)
            for name in graphs
            if name.startswith(self.INVESTIGATION_PREFIX)
        ]

    def delete_investigation(self, investigation_id: str) -> None:
        """Delete an investigation graph if it exists."""
        db = self._require_db()
        graph_name = self.graph_name(investigation_id)
        if graph_name not in db.list_graphs():
            return
        graph = db.select_graph(graph_name)
        graph.delete()

    def count_entities(self, investigation_id: str) -> int:
        """Count entities in an investigation graph."""
        graph = self.create_investigation_graph(investigation_id)
        result = graph.query("MATCH (n:Entity) RETURN COUNT(n)").result_set
        if not result:
            return 0
        return int(result[0][0])

    @staticmethod
    def _normalize_properties(properties: dict[str, Any]) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {}
        for key, value in properties.items():
            if key in {"id", "schema"}:
                continue

            prop_name = key.removeprefix("_")
            if isinstance(value, list):
                normalized[prop_name] = [str(v) for v in value]
            elif value is None:
                normalized[prop_name] = []
            else:
                normalized[prop_name] = [str(value)]

        return normalized

    def get_graph_page(self, investigation_id: str, skip: int = 0, limit: int = 500) -> GraphPage:
        """Get paginated graph data for an investigation."""
        graph = self.create_investigation_graph(investigation_id)

        node_rows = graph.query(
            "MATCH (n:Entity) RETURN n ORDER BY n.id SKIP $skip LIMIT $limit",
            params={"skip": skip, "limit": limit},
        ).result_set
        edge_rows = graph.query(
            "MATCH (a:Entity)-[r]->(b:Entity) "
            "RETURN toString(ID(r)), a.id, b.id, type(r), properties(r) "
            "ORDER BY a.id, b.id SKIP $skip LIMIT $limit",
            params={"skip": skip, "limit": limit},
        ).result_set

        total_nodes = graph.query("MATCH (n:Entity) RETURN COUNT(n)").result_set
        total_edges = graph.query("MATCH (:Entity)-[r]->(:Entity) RETURN COUNT(r)").result_set

        nodes = [
            GraphNode(
                id=str(row[0].properties.get("id", "")),
                schema=str(row[0].properties.get("schema", "Thing")),
                label=(row[0].properties.get("_name") or [row[0].properties.get("id", "")])[0],
                properties=self._normalize_properties(row[0].properties),
            )
            for row in node_rows
        ]

        edges = [
            GraphEdge(
                id=str(row[0]),
                source=str(row[1]),
                target=str(row[2]),
                schema=str(row[3]),
                label=str(row[3]),
                properties=self._normalize_properties(row[4] or {}),
            )
            for row in edge_rows
        ]

        return GraphPage(
            nodes=nodes,
            edges=edges,
            total_nodes=int(total_nodes[0][0]) if total_nodes else 0,
            total_edges=int(total_edges[0][0]) if total_edges else 0,
        )

    def check_connection(self) -> bool:
        """Return whether FalkorDB is reachable."""
        try:
            db = self._require_db()
        except GraphServiceError:
            return False
        try:
            db.list_graphs()
        except (RuntimeError, OSError):  # pragma: no cover - network/driver failures
            return False
        return True
