"""Durable document extraction workflow orchestration using DBOS."""

from __future__ import annotations

from threading import Lock
from typing import Any, Protocol, cast
from uuid import uuid4

import logfire
from dbos import DBOS

from app.config import settings
from app.core.entity_service import EntityService
from app.core.extraction.document_service import DocumentService
from app.core.extraction.extraction_service import ExtractionService
from app.core.ftm_service import FTMService
from app.core.graph_service import GraphService
from app.core.storage_service import StorageService
from app.models.entity import EntityCreate, EntityUpdate


class QueryResultProtocol(Protocol):
    result_set: list[list[object]]


class GraphProtocol(Protocol):
    def query(self, query: str, params: dict[str, object] | None = None) -> QueryResultProtocol: ...


DBOS_STATE = {"launched": False}
DBOS_INIT_LOCK = Lock()
RELATION_ENDPOINT_CANDIDATES: dict[str, list[tuple[str, str]]] = {
    "Ownership": [("owner", "asset")],
    "Directorship": [("director", "organization")],
    "Employment": [("employee", "employer"), ("person", "organization")],
    "Associate": [("person", "associate")],
    "Family": [("person", "relative")],
    "Membership": [("member", "organization"), ("person", "organization")],
    "Representation": [("agent", "client"), ("source", "target")],
    "Payment": [("payer", "beneficiary"), ("seller", "buyer")],
    "UnknownLink": [("subject", "object"), ("source", "target")],
}


def _sanitize_relation(schema: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in schema.upper())
    if not cleaned:
        return "RELATED"
    if cleaned[0].isdigit():
        return f"R_{cleaned}"
    return cleaned


def _resolve_entity_ref(graph: GraphProtocol, ref: str, name_to_id: dict[str, str]) -> str | None:
    token = ref.strip()
    if not token:
        return None

    mapped = name_to_id.get(token.casefold())
    if mapped:
        return mapped

    by_id = graph.query(
        "MATCH (n:Entity {id: $entity_id}) RETURN n.id LIMIT 1",
        params={"entity_id": token},
    ).result_set
    if by_id:
        return str(by_id[0][0])

    by_name = graph.query(
        "MATCH (n:Entity) "
        "WHERE any(name IN coalesce(n._name, []) WHERE toLower(name) = toLower($name)) "
        "RETURN n.id LIMIT 1",
        params={"name": token},
    ).result_set
    if by_name:
        resolved = str(by_name[0][0])
        name_to_id[token.casefold()] = resolved
        return resolved

    return None


def _create_edge(  # noqa: PLR0913
    graph: GraphProtocol,
    edge_id: str,
    schema: str,
    source: str,
    target: str,
    properties: dict[str, list[str]],
    proof_document_id: str | None = None,
) -> bool:
    db_properties = {f"_{key}": values for key, values in properties.items()}
    if proof_document_id and "proof" not in properties:
        db_properties["_proof"] = [proof_document_id]
    relation = _sanitize_relation(schema)
    result = graph.query(
        "MATCH (a:Entity {id: $source}), (b:Entity {id: $target}) "
        f"MERGE (a)-[r:{relation} {{id: $edge_id}}]->(b) "
        "SET r.schema = $schema "
        "SET r += $properties "
        "RETURN r",
        params={
            "source": source,
            "target": target,
            "edge_id": edge_id,
            "schema": schema,
            "properties": db_properties,
        },
    ).result_set
    return bool(result)


def _entity_service() -> EntityService:
    return EntityService(graph_service=GraphService(), ftm_service=FTMService())


@DBOS.step()
def download_document_step(investigation_id: str, storage_key: str) -> bytes:
    """Step 1: Download object bytes from RustFS/S3."""
    storage = StorageService()
    return storage.download_bytes(investigation_id, storage_key)


@DBOS.step()
def parse_document_step(content: bytes, filename: str, content_type: str | None) -> dict:
    """Step 2: Parse document with Kreuzberg."""
    parser = DocumentService()
    return parser.extract(content=content, filename=filename, content_type=content_type)


@DBOS.step()
def extract_entities_step(parsed: dict) -> list[dict]:
    """Step 3: Extract entities via LangExtract + Gemini."""
    extractor = ExtractionService()
    return extractor.extract_entities(parsed["content"], parsed["document_type"])


@DBOS.step()
def persist_entities_step(  # noqa: C901, PLR0912, PLR0915
    payload: dict[str, object],
) -> dict:
    """Step 4: Persist parsed document and extracted entities."""
    investigation_id = str(payload.get("investigation_id", ""))
    document_id = str(payload.get("document_id", ""))
    storage_key = str(payload.get("storage_key", ""))
    filename = str(payload.get("filename", ""))
    parsed = payload.get("parsed")
    entities = payload.get("entities")
    if not isinstance(parsed, dict):
        return {
            "processed": 0,
            "nodes_created": 0,
            "edges_created": 0,
            "errors": ["Invalid parsed payload"],
            "document_id": document_id,
        }
    if not isinstance(entities, list):
        return {
            "processed": 0,
            "nodes_created": 0,
            "edges_created": 0,
            "errors": ["Invalid entities payload"],
            "document_id": document_id,
        }

    entity_service = _entity_service()
    storage = StorageService()
    graph = cast(
        "GraphProtocol",
        entity_service.graph_service.create_investigation_graph(investigation_id),
    )

    existing_doc = entity_service.get(investigation_id, document_id)
    if existing_doc is None:
        msg = f"Document entity '{document_id}' not found"
        raise ValueError(msg)

    merged_properties = dict(existing_doc.properties)
    merged_properties.update(
        {
            "fileName": [filename],
            "mimeType": [parsed["mime_type"]],
            "bodyText": [parsed["content"]],
            "sourceUrl": [storage.object_url(investigation_id, storage_key)],
            "processingStatus": ["completed"],
        },
    )
    entity_service.update(
        investigation_id,
        document_id,
        EntityUpdate(properties=merged_properties),
    )

    nodes_created = 0
    edges_created = 0
    errors: list[str] = []
    name_to_id: dict[str, str] = {}

    node_candidates: list[dict] = []
    relation_candidates: list[dict] = []
    for candidate in entities:
        if not isinstance(candidate, dict):
            continue
        schema = str(candidate.get("schema", "")).strip()
        if schema in RELATION_ENDPOINT_CANDIDATES:
            relation_candidates.append(candidate)
        else:
            node_candidates.append(candidate)

    for idx, candidate in enumerate(node_candidates, start=1):
        if not isinstance(candidate, dict):
            errors.append(f"Entity {idx}: invalid candidate")
            continue
        schema = str(candidate.get("schema", "")).strip()
        properties = candidate.get("properties", {})
        if not schema:
            errors.append(f"Entity {idx}: missing schema")
            continue
        try:
            created = entity_service.create(
                investigation_id,
                EntityCreate(schema=schema, properties=properties),
            )
            nodes_created += 1
            names = created.properties.get("name", [])
            if names:
                name_to_id[names[0].casefold()] = created.id
        except (ValueError, RuntimeError, TypeError) as exc:
            errors.append(f"Entity {idx}: {exc}")

    for idx, candidate in enumerate(relation_candidates, start=1):
        schema = str(candidate.get("schema", "")).strip()
        properties = candidate.get("properties", {})
        if not isinstance(properties, dict):
            errors.append(f"Relation {idx}: invalid properties")
            continue

        endpoint_pair = None
        for left_key, right_key in RELATION_ENDPOINT_CANDIDATES.get(schema, []):
            left_values = properties.get(left_key) or []
            right_values = properties.get(right_key) or []
            if left_values and right_values:
                endpoint_pair = (left_key, right_key, str(left_values[0]), str(right_values[0]))
                break

        if endpoint_pair is None:
            errors.append(f"Relation {idx}: missing endpoints")
            continue

        left_key, right_key, left_ref, right_ref = endpoint_pair
        source_id = _resolve_entity_ref(graph, left_ref, name_to_id)
        target_id = _resolve_entity_ref(graph, right_ref, name_to_id)
        if source_id is None or target_id is None:
            errors.append(
                f"Relation {idx}: unresolved endpoints ({left_ref!r} -> {right_ref!r})",
            )
            continue

        edge_properties: dict[str, list[str]] = {}
        for key, value in properties.items():
            if isinstance(value, list):
                edge_properties[key] = [str(item) for item in value]
            else:
                edge_properties[key] = [str(value)]
        edge_properties[left_key] = [source_id]
        edge_properties[right_key] = [target_id]

        edge_id = str(candidate.get("id") or f"rel-{document_id}-{idx}-{uuid4().hex[:8]}")
        created = _create_edge(
            graph=graph,
            edge_id=edge_id,
            schema=schema,
            source=source_id,
            target=target_id,
            properties=edge_properties,
            proof_document_id=document_id,
        )
        if created:
            edges_created += 1
        else:
            errors.append(f"Relation {idx}: could not create edge")

    return {
        "processed": 1,
        "nodes_created": nodes_created,
        "edges_created": edges_created,
        "errors": errors,
        "document_id": document_id,
    }


@DBOS.workflow()
def document_extraction_workflow(
    investigation_id: str,
    document_id: str,
    storage_key: str,
    filename: str,
    content_type: str | None,
) -> dict:
    """Durable workflow: download -> parse -> extract -> persist."""
    content = download_document_step(investigation_id, storage_key)
    parsed = parse_document_step(content, filename, content_type)
    entities = extract_entities_step(parsed)
    return persist_entities_step(
        payload={
            "investigation_id": investigation_id,
            "document_id": document_id,
            "storage_key": storage_key,
            "filename": filename,
            "parsed": parsed,
            "entities": entities,
        },
    )


class ExtractionWorkflowService:
    """Submit and inspect DBOS extraction workflows."""

    def __init__(self) -> None:
        self._init_dbos()

    def _init_dbos(self) -> None:
        if DBOS_STATE["launched"]:
            return
        with DBOS_INIT_LOCK:
            if DBOS_STATE["launched"]:
                return
            config = {
                "name": settings.dbos_app_name,
                "system_database_url": settings.dbos_system_database_url,
            }
            with logfire.span("initialize dbos runtime"):
                DBOS(config=cast("Any", config))
                DBOS.launch()
            DBOS_STATE["launched"] = True

    @logfire.instrument("enqueue extraction workflow", extract_args=False)
    def enqueue(
        self,
        investigation_id: str,
        document_id: str,
        storage_key: str,
        filename: str,
        content_type: str | None,
    ) -> str:
        """Start durable extraction workflow and return workflow ID."""
        handle = DBOS.start_workflow(
            document_extraction_workflow,
            investigation_id,
            document_id,
            storage_key,
            filename,
            content_type,
        )
        return str(getattr(handle, "workflow_id", ""))

    @logfire.instrument("get workflow status", extract_args=False)
    def get_status(self, workflow_id: str) -> dict:
        """Get workflow state and result/error if available."""
        try:
            handle = DBOS.retrieve_workflow(workflow_id)
        except (RuntimeError, ValueError, TypeError):
            return {
                "workflow_id": workflow_id,
                "status": "NOT_FOUND",
                "result": None,
                "error": "Workflow not found",
            }

        status = str(getattr(handle, "status", "UNKNOWN"))
        result = None
        error = None

        try:
            if status.upper() in {"SUCCESS", "COMPLETED"}:
                result = handle.get_result()
        except (RuntimeError, ValueError, TypeError) as exc:
            error = str(exc)

        if status.upper() in {"ERROR", "FAILED", "CANCELLED"} and error is None:
            try:
                handle.get_result()
            except (RuntimeError, ValueError, TypeError) as exc:
                error = str(exc)

        return {
            "workflow_id": workflow_id,
            "status": status,
            "result": result,
            "error": error,
        }
