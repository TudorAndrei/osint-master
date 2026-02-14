"""Ingestion orchestration service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from app.core.cleaning_service import CleaningService
from app.core.ingest.ftm_json import FTMJsonIngestor
from app.models.entity import EntityCreate, EntityUpdate
from app.models.ingest import IngestResult

if TYPE_CHECKING:
    from app.core.entity_service import EntityService

RELATION_ENDPOINT_CANDIDATES: dict[str, list[tuple[str, str]]] = {
    "Ownership": [("owner", "asset"), ("source", "target")],
    "Directorship": [("director", "organization"), ("person", "organization")],
    "Employment": [("employee", "employer"), ("person", "organization")],
    "Associate": [("person", "associate")],
    "Family": [("person", "relative")],
    "Membership": [("member", "organization"), ("person", "organization")],
    "Representation": [("agent", "client"), ("source", "target")],
    "Payment": [("payer", "beneficiary"), ("seller", "buyer")],
    "UnknownLink": [("subject", "object"), ("source", "target")],
}

GENERIC_ENDPOINT_CANDIDATES: list[tuple[str, str]] = [
    ("subject", "object"),
    ("source", "target"),
    ("owner", "asset"),
    ("employee", "employer"),
    ("person", "organization"),
    ("seller", "buyer"),
]

RELATION_PROPERTY_ALIASES: dict[str, dict[str, str]] = {
    "Employment": {"person": "employee", "organization": "employer"},
    "Directorship": {"person": "director"},
    "Membership": {"person": "member"},
    "Ownership": {"source": "owner", "target": "asset"},
    "Representation": {"source": "agent", "target": "client"},
    "Payment": {"seller": "payer", "buyer": "beneficiary"},
    "UnknownLink": {"source": "subject", "target": "object"},
}


@dataclass(slots=True)
class EdgeCandidate:
    edge_id: str
    schema: str
    source: str
    target: str
    left_key: str
    right_key: str
    properties: dict[str, list[str]]


class IngestService:
    """Parse and persist uploaded FTM files."""

    def __init__(self, entity_service: EntityService) -> None:
        self.entity_service = entity_service
        self.ingestor = FTMJsonIngestor()
        self.cleaning_service = CleaningService()

    @staticmethod
    def _sanitize_relation(schema: str) -> str:
        cleaned = "".join(ch if ch.isalnum() else "_" for ch in schema.upper())
        if not cleaned:
            return "RELATED"
        if cleaned[0].isdigit():
            return f"R_{cleaned}"
        return cleaned

    @staticmethod
    def _normalize_relation_properties(
        schema: str, properties: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        normalized: dict[str, list[str]] = dict(properties)
        aliases = RELATION_PROPERTY_ALIASES.get(schema, {})
        for alias, canonical in aliases.items():
            alias_values = normalized.get(alias) or []
            canonical_values = normalized.get(canonical) or []
            if alias_values and not canonical_values:
                normalized[canonical] = alias_values
        return normalized

    @staticmethod
    def _edge_endpoints(
        schema: str,
        properties: dict[str, list[str]],
    ) -> tuple[str, str, str, str] | None:
        pairs = RELATION_ENDPOINT_CANDIDATES.get(schema, []) + GENERIC_ENDPOINT_CANDIDATES
        for left_key, right_key in pairs:
            left = properties.get(left_key) or []
            right = properties.get(right_key) or []
            if left and right:
                return left_key, right_key, left[0], right[0]
        return None

    def _resolve_entity_ref(
        self,
        investigation_id: str,
        token: str,
        cache: dict[str, str],
    ) -> str | None:
        ref = token.strip()
        if not ref:
            return None

        folded = ref.casefold()
        cached = cache.get(folded)
        if cached:
            return cached

        graph = self.entity_service.graph_service.create_investigation_graph(investigation_id)
        by_id_result = graph.query(
            "MATCH (n:Entity {id: $entity_id}) RETURN n.id LIMIT 1",
            params={"entity_id": ref},
        )
        by_id = getattr(by_id_result, "result_set", [])
        if by_id:
            resolved = str(by_id[0][0])
            cache[folded] = resolved
            return resolved

        by_name_result = graph.query(
            "MATCH (n:Entity) "
            "WHERE any(name IN coalesce(n._name, []) WHERE toLower(name) = toLower($name)) "
            "RETURN n.id LIMIT 1",
            params={"name": ref},
        )
        by_name = getattr(by_name_result, "result_set", [])
        if by_name:
            resolved = str(by_name[0][0])
            cache[folded] = resolved
            return resolved
        return None

    def _create_edge(self, investigation_id: str, candidate: EdgeCandidate) -> bool:
        candidate.properties[candidate.left_key] = [candidate.source]
        candidate.properties[candidate.right_key] = [candidate.target]
        self.entity_service.ftm_service.validate_entity_input(
            candidate.schema, candidate.properties
        )

        graph = self.entity_service.graph_service.create_investigation_graph(investigation_id)
        db_properties = {f"_{key}": values for key, values in candidate.properties.items()}
        relation = self._sanitize_relation(candidate.schema)
        result = graph.query(
            "MATCH (a:Entity {id: $source}), (b:Entity {id: $target}) "
            f"MERGE (a)-[r:{relation} {{id: $edge_id}}]->(b) "
            "SET r.schema = $schema "
            "SET r += $properties "
            "RETURN r",
            params={
                "source": candidate.source,
                "target": candidate.target,
                "edge_id": candidate.edge_id,
                "schema": candidate.schema,
                "properties": db_properties,
            },
        )
        rows = getattr(result, "result_set", [])
        return bool(rows)

    def _validate_extension(self, filename: str) -> None:
        extension = Path(filename).suffix.lower()
        if extension and extension not in self.ingestor.supported_extensions:
            supported = ", ".join(self.ingestor.supported_extensions)
            msg = f"Unsupported file extension '{extension}'. Supported: {supported}"
            raise ValueError(msg)

    def _edge_candidate(  # noqa: PLR0913
        self,
        investigation_id: str,
        idx: int,
        schema: str,
        entity_id: str | None,
        properties: dict[str, list[str]],
        ref_cache: dict[str, str],
    ) -> EdgeCandidate | None:
        normalized = self._normalize_relation_properties(schema, properties)
        endpoints = self._edge_endpoints(schema, normalized)
        if endpoints is None:
            return None
        left_key, right_key, left, right = endpoints
        source = self._resolve_entity_ref(investigation_id, left, ref_cache)
        target = self._resolve_entity_ref(investigation_id, right, ref_cache)
        if source is None or target is None:
            return None
        edge_id = entity_id or f"edge-{idx}"
        return EdgeCandidate(
            edge_id=edge_id,
            schema=schema,
            source=source,
            target=target,
            left_key=left_key,
            right_key=right_key,
            properties=normalized,
        )

    def _upsert_entity(
        self,
        idx: int,
        investigation_id: str,
        schema: str,
        entity_id: str | None,
        properties: dict[str, list[str]],
    ) -> tuple[int, list[str]]:
        errors: list[str] = []
        try:
            self.entity_service.create(
                investigation_id,
                EntityCreate(id=entity_id, schema=schema, properties=properties),
            )
        except ValueError:
            if entity_id is None:
                errors.append(f"Record {idx}: invalid entity payload")
                return 0, errors
            try:
                self.entity_service.update(
                    investigation_id,
                    entity_id,
                    payload=EntityUpdate(properties=properties),
                )
            except (ValueError, RuntimeError, TypeError) as exc:
                errors.append(f"Record {idx}: {exc}")
        except (RuntimeError, TypeError) as exc:
            errors.append(f"Record {idx}: {exc}")
        else:
            return 1, errors
        return 0, errors

    def ingest_file(self, investigation_id: str, filename: str, content: bytes) -> IngestResult:
        """Ingest a supported FTM JSON file into the investigation graph."""
        self._validate_extension(filename)

        processed = 0
        nodes_created = 0
        edges_created = 0
        errors: list[str] = []
        ref_cache: dict[str, str] = {}

        set_filename_hint = getattr(self.ingestor, "set_filename_hint", None)
        if callable(set_filename_hint):
            set_filename_hint(filename)
        records = cast("list[dict]", list(self.ingestor.ingest(content)))

        for idx, record in enumerate(records, start=1):
            processed += 1
            schema = str(record.get("schema", "")).strip()
            if not schema:
                errors.append(f"Record {idx}: missing schema")
                continue

            properties = record.get("properties") or {}
            if not isinstance(properties, dict):
                errors.append(f"Record {idx}: invalid properties")
                continue
            properties = self.cleaning_service.clean_properties(properties)

            entity_id = str(record.get("id") or "").strip() or None
            candidate = self._edge_candidate(
                investigation_id,
                idx,
                schema,
                entity_id,
                properties,
                ref_cache,
            )

            if candidate is not None:
                try:
                    created = self._create_edge(investigation_id, candidate)
                except (ValueError, RuntimeError, TypeError) as exc:
                    errors.append(f"Record {idx}: {exc}")
                    continue
                if created:
                    edges_created += 1
                else:
                    msg = (
                        f"Record {idx}: could not create edge "
                        f"({candidate.source} -> {candidate.target})"
                    )
                    errors.append(msg)
                continue

            if schema in RELATION_ENDPOINT_CANDIDATES:
                errors.append(f"Record {idx}: unresolved relation endpoints")
                continue

            created_nodes, upsert_errors = self._upsert_entity(
                idx,
                investigation_id,
                schema,
                entity_id,
                properties,
            )
            nodes_created += created_nodes
            errors.extend(upsert_errors)

        return IngestResult(
            processed=processed,
            nodes_created=nodes_created,
            edges_created=edges_created,
            errors=errors,
        )
