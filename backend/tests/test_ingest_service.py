"""Tests for enhanced relation ingestion behavior."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from app.core.ingest_service import IngestService


@dataclass
class FakeResult:
    result_set: list[list[object]]


class FakeGraph:
    def __init__(self) -> None:
        self.nodes_by_id = {
            "person-1": {"id": "person-1", "name": ["John Doe"]},
            "company-1": {"id": "company-1", "name": ["Acme Corp"]},
        }
        self.edges: list[dict[str, Any]] = []

    def add_node(self, entity_id: str, properties: dict[str, list[str]]) -> None:
        self.nodes_by_id[entity_id] = {
            "id": entity_id,
            "name": properties.get("name", []),
        }

    def query(self, query: str, params: dict[str, object] | None = None) -> FakeResult:
        params = params or {}

        if "MATCH (n:Entity {id: $entity_id}) RETURN n.id" in query:
            entity_id = str(params.get("entity_id", ""))
            if entity_id in self.nodes_by_id:
                return FakeResult([[entity_id]])
            return FakeResult([])

        if "WHERE any(name IN coalesce(n._name, [])" in query:
            name = str(params.get("name", "")).casefold()
            for node in self.nodes_by_id.values():
                first_name = str((node.get("name") or [""])[0]).casefold()
                if first_name == name:
                    return FakeResult([[str(node["id"])]])
            return FakeResult([])

        if "MERGE (a)-[r:" in query:
            self.edges.append(
                {
                    "source": str(params.get("source", "")),
                    "target": str(params.get("target", "")),
                    "schema": str(params.get("schema", "")),
                    "properties": params.get("properties", {}),
                }
            )
            return FakeResult([[{"id": str(params.get("edge_id", "edge"))}]])

        raise AssertionError(f"Unexpected query: {query}")


class FakeGraphService:
    def __init__(self) -> None:
        self.graph = FakeGraph()

    def create_investigation_graph(self, _: str) -> FakeGraph:
        return self.graph


class FakeFTMService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, list[str]]]] = []

    def validate_entity_input(self, schema: str, properties: dict[str, list[str]]) -> None:
        self.calls.append((schema, properties))


class FakeEntityService:
    def __init__(self) -> None:
        self.graph_service = FakeGraphService()
        self.ftm_service = FakeFTMService()

    def create(self, investigation_id: str, payload: object) -> object:
        entity_id = (
            getattr(payload, "id", None) or f"node-{len(self.graph_service.graph.nodes_by_id) + 1}"
        )
        properties = dict(getattr(payload, "properties", {}))
        self.graph_service.graph.add_node(entity_id, properties)
        return type("Entity", (), {"id": entity_id, "properties": properties})()

    def update(self, investigation_id: str, entity_id: str, payload: object) -> object:
        properties = dict(getattr(payload, "properties", {}))
        self.graph_service.graph.add_node(entity_id, properties)
        return type("Entity", (), {"id": entity_id, "properties": properties})()


def _fixture_bytes(name: str) -> bytes:
    path = Path(__file__).parent / "fixtures" / name
    return path.read_bytes()


def test_ingest_maps_employment_aliases_and_resolves_names() -> None:
    entity_service = FakeEntityService()
    service = IngestService(entity_service=cast(Any, entity_service))

    records = [
        {
            "id": "rel-1",
            "schema": "Employment",
            "properties": {
                "person": ["John Doe"],
                "organization": ["Acme Corp"],
                "role": ["CEO"],
                "startDate": ["2021-07"],
                "confidence": ["0.93"],
            },
        }
    ]
    service.ingestor.ingest = lambda _content: records  # type: ignore[method-assign]

    result = service.ingest_file("inv-1", "relations.json", b"[]")

    assert result.edges_created == 1
    assert result.nodes_created == 0
    assert result.errors == []

    edge = entity_service.graph_service.graph.edges[0]
    assert edge["source"] == "person-1"
    assert edge["target"] == "company-1"
    assert edge["schema"] == "Employment"

    schema, validated_props = entity_service.ftm_service.calls[0]
    assert schema == "Employment"
    assert validated_props["employee"] == ["person-1"]
    assert validated_props["employer"] == ["company-1"]


def test_ingest_rejects_relations_with_unresolved_endpoints() -> None:
    entity_service = FakeEntityService()
    service = IngestService(entity_service=cast(Any, entity_service))

    records = [
        {
            "id": "rel-2",
            "schema": "Ownership",
            "properties": {
                "owner": ["Unknown Owner"],
                "asset": ["Missing Asset"],
            },
        }
    ]
    service.ingestor.ingest = lambda _content: records  # type: ignore[method-assign]

    result = service.ingest_file("inv-1", "relations.json", b"[]")

    assert result.edges_created == 0
    assert any("unresolved relation endpoints" in msg for msg in result.errors)


def test_ingest_sec_excerpt_fixture_end_to_end_relations() -> None:
    entity_service = FakeEntityService()
    service = IngestService(entity_service=cast(Any, entity_service))

    content = _fixture_bytes("sec_excerpt_amazon_item13_entities.ndjson")
    result = service.ingest_file("inv-sec", "sec_excerpt_amazon_item13_entities.ndjson", content)

    assert result.processed == 8
    assert result.nodes_created == 4
    assert result.edges_created == 4
    assert result.errors == []

    edges = entity_service.graph_service.graph.edges
    assert any(edge["schema"] == "Employment" for edge in edges)
    assert any(edge["schema"] == "Directorship" for edge in edges)
    assert any(edge["schema"] == "Ownership" for edge in edges)
    assert any(edge["schema"] == "Representation" for edge in edges)
