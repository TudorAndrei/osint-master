"""Entity CRUD and expansion service."""

from __future__ import annotations

from difflib import SequenceMatcher
from itertools import combinations
from typing import TYPE_CHECKING, Any, Protocol, cast
from uuid import uuid4

from app.models.entity import (
    DuplicateCandidate,
    Entity,
    EntityCreate,
    EntityExpand,
    EntityUpdate,
    MergeEntitiesResponse,
)

if TYPE_CHECKING:
    from app.core.ftm_service import FTMService
    from app.core.graph_service import GraphService


class NodeProtocol(Protocol):
    properties: dict[str, Any]


class QueryResultProtocol(Protocol):
    result_set: list[list[object]]


class GraphProtocol(Protocol):
    def query(self, query: str, params: dict[str, object] | None = None) -> QueryResultProtocol: ...


class EntityService:
    """Manage entities within an investigation graph."""

    def __init__(self, graph_service: GraphService, ftm_service: FTMService) -> None:
        self.graph_service = graph_service
        self.ftm_service = ftm_service

    def _graph(self, investigation_id: str) -> GraphProtocol:
        return cast(
            "GraphProtocol",
            self.graph_service.create_investigation_graph(investigation_id),
        )

    @staticmethod
    def _normalize_properties(properties: dict[str, Any]) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = {}
        for key, value in properties.items():
            if key in {"id", "schema"}:
                continue

            prop_name = key.removeprefix("_")

            if isinstance(value, list):
                normalized[prop_name] = [str(item) for item in value]
                continue

            if value is None:
                normalized[prop_name] = []
                continue

            normalized[prop_name] = [str(value)]

        return normalized

    @staticmethod
    def _db_properties(properties: dict[str, list[str]]) -> dict[str, list[str]]:
        return {f"_{key}": values for key, values in properties.items()}

    def _to_entity(self, node: NodeProtocol) -> Entity:
        props = self._normalize_properties(node.properties)
        return Entity(
            id=str(node.properties.get("id", "")),
            schema=node.properties.get("schema", "Thing"),
            properties=props,
        )

    @staticmethod
    def _set_entity_properties(
        graph: GraphProtocol, entity_id: str, properties: dict[str, list[str]]
    ) -> None:
        existing = graph.query(
            "MATCH (n:Entity {id: $entity_id}) RETURN n LIMIT 1",
            params={"entity_id": entity_id},
        ).result_set
        if not existing:
            msg = f"Entity '{entity_id}' not found"
            raise ValueError(msg)

        node: NodeProtocol = cast("NodeProtocol", existing[0][0])
        removable_keys = [key for key in node.properties if key not in {"id", "schema"}]
        remove_clause = ""
        if removable_keys:
            remove_clause = "REMOVE " + ", ".join(f"n.{key}" for key in removable_keys)

        query = f"MATCH (n:Entity {{id: $entity_id}}) {remove_clause} SET n += $properties RETURN n"
        db_properties = {f"_{key}": values for key, values in properties.items()}
        graph.query(
            query,
            params={"entity_id": entity_id, "properties": db_properties},
        )

    @staticmethod
    def _similarity(left: Entity, right: Entity) -> tuple[float, str]:
        left_name = (left.properties.get("name") or [left.id])[0]
        right_name = (right.properties.get("name") or [right.id])[0]
        name_similarity = SequenceMatcher(None, left_name.casefold(), right_name.casefold()).ratio()

        score = 0.7 * name_similarity
        reasons = [f"name similarity {name_similarity:.2f}"]

        comparable_fields = [
            "birthDate",
            "country",
            "nationality",
            "jurisdiction",
            "registrationNumber",
            "email",
            "innCode",
            "vatCode",
        ]
        overlap_count = 0
        checked_fields = 0
        for field in comparable_fields:
            left_values = {value.casefold() for value in left.properties.get(field, [])}
            right_values = {value.casefold() for value in right.properties.get(field, [])}
            if not left_values or not right_values:
                continue
            checked_fields += 1
            if left_values & right_values:
                overlap_count += 1

        if checked_fields > 0:
            overlap_ratio = overlap_count / checked_fields
            score += 0.3 * overlap_ratio
            reasons.append(f"attribute overlap {overlap_ratio:.2f}")

        return min(score, 1.0), ", ".join(reasons)

    @staticmethod
    def _merge_properties(entities: list[Entity]) -> dict[str, list[str]]:
        merged: dict[str, list[str]] = {}
        for entity in entities:
            for key, values in entity.properties.items():
                merged.setdefault(key, [])
                for value in values:
                    if value not in merged[key]:
                        merged[key].append(value)
        return merged

    @staticmethod
    def _recreate_edge(
        graph: GraphProtocol,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict[str, Any],
    ) -> None:
        relation = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in rel_type)
        edge_id = properties.get("id")
        if edge_id is not None:
            graph.query(
                f"MATCH (a:Entity {{id: $source}}), (b:Entity {{id: $target}}) "
                f"MERGE (a)-[r:{relation} {{id: $edge_id}}]->(b) "
                "SET r += $properties",
                params={
                    "source": source_id,
                    "target": target_id,
                    "edge_id": str(edge_id),
                    "properties": properties,
                },
            )
            return

        graph.query(
            f"MATCH (a:Entity {{id: $source}}), (b:Entity {{id: $target}}) "
            f"CREATE (a)-[r:{relation}]->(b) "
            "SET r += $properties",
            params={"source": source_id, "target": target_id, "properties": properties},
        )

    def _get_node(self, graph: GraphProtocol, entity_id: str) -> NodeProtocol | None:
        result = graph.query(
            "MATCH (n:Entity {id: $entity_id}) RETURN n LIMIT 1",
            params={"entity_id": entity_id},
        ).result_set
        if not result:
            return None
        return result[0][0]  # type: ignore[return-value]

    def create(self, investigation_id: str, payload: EntityCreate) -> Entity:
        schema_name = payload.schema_
        properties = payload.properties
        self.ftm_service.validate_entity_input(schema_name, properties)

        graph = self._graph(investigation_id)
        entity_id = payload.id or str(uuid4())

        if self._get_node(graph, entity_id) is not None:
            msg = f"Entity '{entity_id}' already exists"
            raise ValueError(msg)

        db_properties = self._db_properties(properties)
        result = graph.query(
            "CREATE (n:Entity {id: $entity_id, schema: $schema}) SET n += $properties RETURN n",
            params={"entity_id": entity_id, "schema": schema_name, "properties": db_properties},
        ).result_set
        return self._to_entity(result[0][0])  # type: ignore[arg-type]

    def list(self, investigation_id: str, search: str | None = None) -> list[Entity]:
        graph = self._graph(investigation_id)
        if search:
            result = graph.query(
                "MATCH (n:Entity) "
                "WHERE toLower(n.id) CONTAINS toLower($search) "
                "OR toLower(toString(n._name)) CONTAINS toLower($search) "
                "RETURN n ORDER BY n.id",
                params={"search": search},
            ).result_set
        else:
            result = graph.query("MATCH (n:Entity) RETURN n ORDER BY n.id").result_set

        return [self._to_entity(row[0]) for row in result]  # type: ignore[arg-type]

    def get(self, investigation_id: str, entity_id: str) -> Entity | None:
        graph = self._graph(investigation_id)
        node = self._get_node(graph, entity_id)
        if node is None:
            return None
        return self._to_entity(node)

    def update(self, investigation_id: str, entity_id: str, payload: EntityUpdate) -> Entity | None:
        graph = self._graph(investigation_id)
        node = self._get_node(graph, entity_id)
        if node is None:
            return None

        schema_name = str(node.properties.get("schema", "Thing"))
        self.ftm_service.validate_entity_input(schema_name, payload.properties)

        self._set_entity_properties(graph, entity_id, payload.properties)
        result = graph.query(
            "MATCH (n:Entity {id: $entity_id}) RETURN n LIMIT 1",
            params={"entity_id": entity_id},
        ).result_set
        return self._to_entity(result[0][0])  # type: ignore[arg-type]

    def delete(self, investigation_id: str, entity_id: str) -> bool:
        graph = self._graph(investigation_id)
        result = graph.query(
            "MATCH (n:Entity {id: $entity_id}) WITH n LIMIT 1 DETACH DELETE n RETURN 1",
            params={"entity_id": entity_id},
        ).result_set
        return bool(result)

    def expand(self, investigation_id: str, entity_id: str) -> EntityExpand | None:
        graph = self._graph(investigation_id)
        result = graph.query(
            "MATCH (n:Entity {id: $entity_id}) "
            "OPTIONAL MATCH (n)-[r]-(m:Entity) "
            "RETURN n, "
            "collect(DISTINCT m) AS neighbors, "
            "collect(DISTINCT {"
            "id: toString(ID(r)), "
            "source: startNode(r).id, "
            "target: endNode(r).id, "
            "schema: type(r), "
            "properties: properties(r)"
            "}) AS edges",
            params={"entity_id": entity_id},
        ).result_set
        if not result:
            return None

        node, raw_neighbors, raw_edges = result[0]
        neighbor_nodes = cast("list[NodeProtocol | None]", raw_neighbors)
        edge_items = cast("list[dict[str, object]]", raw_edges)
        neighbors = [
            self._to_entity(neighbor)  # type: ignore[arg-type]
            for neighbor in neighbor_nodes
            if neighbor is not None and str(neighbor.properties.get("id", "")) != entity_id
        ]
        edges = [edge for edge in edge_items if edge.get("id") is not None]

        return EntityExpand(entity=self._to_entity(node), neighbors=neighbors, edges=edges)  # type: ignore[arg-type]

    def find_duplicates(
        self,
        investigation_id: str,
        schema: str | None = None,
        threshold: float = 0.7,
        limit: int = 100,
    ) -> list[DuplicateCandidate]:
        entities = self.list(investigation_id)
        if schema:
            entities = [entity for entity in entities if entity.schema_ == schema]

        candidates: list[DuplicateCandidate] = []
        for left, right in combinations(entities, 2):
            if left.schema_ != right.schema_:
                continue
            similarity, reason = self._similarity(left, right)
            if similarity < threshold:
                continue
            candidates.append(
                DuplicateCandidate(
                    left=left,
                    right=right,
                    similarity=round(similarity, 4),
                    reason=reason,
                )
            )

        candidates.sort(key=lambda candidate: candidate.similarity, reverse=True)
        return candidates[:limit]

    def merge_entities(  # noqa: C901
        self,
        investigation_id: str,
        source_ids: list[str],
        target_id: str,
        merged_properties: dict[str, list[str]] | None,
    ) -> MergeEntitiesResponse:
        unique_ids = [entity_id.strip() for entity_id in source_ids if entity_id.strip()]
        unique_ids = list(dict.fromkeys(unique_ids))
        if len(unique_ids) < self.MIN_MERGE_SOURCE_IDS:
            msg = "At least two source_ids are required"
            raise ValueError(msg)
        if target_id not in unique_ids:
            msg = "target_id must be one of source_ids"
            raise ValueError(msg)

        graph = self._graph(investigation_id)
        entities: dict[str, Entity] = {}
        for entity_id in unique_ids:
            entity = self.get(investigation_id, entity_id)
            if entity is None:
                msg = f"Entity '{entity_id}' not found"
                raise ValueError(msg)
            entities[entity_id] = entity

        schema_names = {entity.schema_ for entity in entities.values()}
        if len(schema_names) != 1:
            msg = "All source entities must have the same schema"
            raise ValueError(msg)

        final_properties = merged_properties or self._merge_properties(list(entities.values()))
        schema_name = next(iter(schema_names))
        self.ftm_service.validate_entity_input(schema_name, final_properties)

        for source_id in unique_ids:
            if source_id == target_id:
                continue

            outgoing = graph.query(
                "MATCH (source:Entity {id: $source_id})-[r]->(other:Entity) "
                "RETURN type(r), properties(r), other.id",
                params={"source_id": source_id},
            ).result_set
            incoming = graph.query(
                "MATCH (other:Entity)-[r]->(source:Entity {id: $source_id}) "
                "RETURN type(r), properties(r), other.id",
                params={"source_id": source_id},
            ).result_set

            for row in outgoing:
                rel_type = str(row[0])
                rel_props = cast("dict[str, Any]", row[1] or {})
                other_id = str(row[2])
                if other_id == target_id:
                    continue
                self._recreate_edge(graph, target_id, other_id, rel_type, rel_props)

            for row in incoming:
                rel_type = str(row[0])
                rel_props = cast("dict[str, Any]", row[1] or {})
                other_id = str(row[2])
                if other_id == target_id:
                    continue
                self._recreate_edge(graph, other_id, target_id, rel_type, rel_props)

            graph.query(
                "MATCH (n:Entity {id: $entity_id}) DETACH DELETE n",
                params={"entity_id": source_id},
            )

        self._set_entity_properties(graph, target_id, final_properties)
        merged = self.get(investigation_id, target_id)
        if merged is None:
            msg = f"Merged entity '{target_id}' not found"
            raise RuntimeError(msg)

        merged_ids = [entity_id for entity_id in unique_ids if entity_id != target_id]
        return MergeEntitiesResponse(target=merged, merged_source_ids=merged_ids)

    MIN_MERGE_SOURCE_IDS = 2
