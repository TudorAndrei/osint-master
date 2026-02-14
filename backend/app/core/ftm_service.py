"""FollowTheMoney schema and entity operations."""

from __future__ import annotations

import re

try:
    from followthemoney import model as ftm_model  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    ftm_model = None

from app.models.schema import Schema, SchemaDetail, SchemaProperty

FALLBACK_SCHEMATA = [
    Schema(
        name="Thing",
        label="Thing",
        plural="Things",
        abstract=True,
        matchable=False,
    ),
    Schema(
        name="Person",
        label="Person",
        plural="People",
        abstract=False,
        matchable=True,
    ),
    Schema(
        name="Company",
        label="Company",
        plural="Companies",
        abstract=False,
        matchable=True,
    ),
    Schema(
        name="Document",
        label="Document",
        plural="Documents",
        abstract=False,
        matchable=False,
    ),
    Schema(
        name="Ownership",
        label="Ownership",
        plural="Ownerships",
        abstract=False,
        matchable=False,
    ),
]

ISO_DATE_PATTERN = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
CUSTOM_ALLOWED_PROPERTIES = {
    "confidence",
    "charStart",
    "charEnd",
    "relationGroup",
}


class FTMService:
    """Service for FTM schema and entity operations."""

    def __init__(self) -> None:
        self._model = ftm_model

    def list_schemata(self) -> list[Schema]:
        """List available schemata from FTM, with a fallback set."""
        if self._model is None:
            return FALLBACK_SCHEMATA

        return [
            Schema(
                name=schema.name,
                label=schema.label,
                plural=schema.plural,
                abstract=schema.abstract,
                matchable=schema.matchable,
            )
            for schema in self._model.schemata.values()
        ]

    def get_schema(self, name: str) -> SchemaDetail | None:
        """Get detailed schema information by name."""
        if self._model is None:
            fallback = {schema.name: schema for schema in FALLBACK_SCHEMATA}.get(name)
            if fallback is None:
                return None
            return SchemaDetail(**fallback.model_dump(), properties=[])

        schema = self._model.get(name)
        if schema is None:
            return None

        return SchemaDetail(
            name=schema.name,
            label=schema.label,
            plural=schema.plural,
            abstract=schema.abstract,
            matchable=schema.matchable,
            properties=[
                SchemaProperty(
                    name=prop.name,
                    label=prop.label,
                    type=prop.type.name,
                    multiple=prop.multiple,
                )
                for prop in schema.properties.values()
            ],
        )

    def schema_exists(self, name: str) -> bool:
        """Return whether a schema exists."""
        return self.get_schema(name) is not None

    def validate_entity_input(  # noqa: C901
        self,
        schema: str,
        properties: dict[str, list[str]],
    ) -> None:
        """Validate schema and properties using FTM when available."""
        for key, values in properties.items():
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                msg = f"Property '{key}' must be a list of strings"
                raise ValueError(msg)

        if self._model is None:
            if not schema.strip():
                msg = "Schema must be a non-empty string"
                raise ValueError(msg)
            self._validate_common_types(properties)
            return

        if not self.schema_exists(schema):
            msg = f"Schema '{schema}' is not available"
            raise ValueError(msg)

        schema_model = self._model.get(schema)
        if schema_model is None:
            msg = f"Schema '{schema}' is not available"
            raise ValueError(msg)

        entity = self._model.make_entity(schema)
        for key, values in properties.items():
            if key.startswith("_") or key in CUSTOM_ALLOWED_PROPERTIES:
                continue

            prop = schema_model.properties.get(key)
            if prop is None:
                continue

            prop_type = prop.type.name
            for value in values:
                self._validate_known_type(key, value, prop_type)
                entity.add(key, value)

    @staticmethod
    def _validate_known_type(key: str, value: str, prop_type: str) -> None:
        if prop_type == "date" and value and ISO_DATE_PATTERN.match(value) is None:
            msg = f"Property '{key}' must be ISO date format (YYYY, YYYY-MM, or YYYY-MM-DD)"
            raise ValueError(msg)

        if prop_type == "number":
            try:
                float(value)
            except ValueError as exc:
                msg = f"Property '{key}' must be numeric"
                raise ValueError(msg) from exc

    @staticmethod
    def _validate_common_types(properties: dict[str, list[str]]) -> None:
        for key, values in properties.items():
            if key in {"startDate", "endDate", "date", "retrievedAt", "modifiedAt"}:
                for value in values:
                    if value and ISO_DATE_PATTERN.match(value) is None:
                        msg = (
                            f"Property '{key}' must be ISO date format "
                            "(YYYY, YYYY-MM, or YYYY-MM-DD)"
                        )
                        raise ValueError(msg)

            if key in {"amount", "amountUsd", "amountEur", "confidence"}:
                for value in values:
                    try:
                        float(value)
                    except ValueError as exc:
                        msg = f"Property '{key}' must be numeric"
                        raise ValueError(msg) from exc
