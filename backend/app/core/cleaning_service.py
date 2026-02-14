"""Entity property normalization helpers."""

from __future__ import annotations

from datetime import UTC, datetime

DATE_INPUT_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%m-%d-%Y",
)

COUNTRY_CODE_LENGTH = 2
YEAR_LENGTH = 4
YEAR_MONTH_LENGTH = 7
MAX_MONTH_VALUE = 12

DATE_FIELDS = {
    "birthDate",
    "deathDate",
    "date",
    "startDate",
    "endDate",
    "incorporationDate",
    "dissolutionDate",
    "retrievedAt",
    "modifiedAt",
}

NUMERIC_FIELDS = {
    "amount",
    "amountUsd",
    "amountEur",
    "confidence",
    "percentage",
    "charStart",
    "charEnd",
}

LOWERCASE_FIELDS = {
    "email",
    "sourceUrl",
    "website",
}

COUNTRY_FIELDS = {
    "country",
    "countries",
    "nationality",
    "jurisdiction",
}


class CleaningService:
    """Clean entity properties after extraction and ingestion."""

    def clean_entity(self, entity: dict) -> dict:
        """Return a cleaned copy of an entity dict."""
        cleaned = dict(entity)
        properties = entity.get("properties")
        if not isinstance(properties, dict):
            return cleaned
        cleaned["properties"] = self.clean_properties(properties)
        return cleaned

    def clean_properties(self, properties: dict[str, object]) -> dict[str, list[str]]:
        """Normalize and deduplicate property values."""
        cleaned: dict[str, list[str]] = {}
        for key, raw_values in properties.items():
            values = self._ensure_list(raw_values)
            normalized = [
                normalized_value
                for value in values
                if (normalized_value := self._normalize_value(key, value)) is not None
            ]
            deduped = self._dedupe(normalized)
            if deduped:
                cleaned[key] = deduped
        return cleaned

    @staticmethod
    def _ensure_list(raw_values: object) -> list[str]:
        if isinstance(raw_values, list):
            return [str(value) for value in raw_values]
        if raw_values is None:
            return []
        return [str(raw_values)]

    def _normalize_value(self, key: str, value: str) -> str | None:
        text = " ".join(value.strip().split())
        if not text:
            return None

        if key in DATE_FIELDS:
            parsed = self._normalize_date(text)
            return parsed if parsed is not None else text

        if key in NUMERIC_FIELDS:
            parsed = self._normalize_number(text)
            return parsed if parsed is not None else text

        if key in COUNTRY_FIELDS:
            return text.lower() if len(text) == COUNTRY_CODE_LENGTH else text

        if key in LOWERCASE_FIELDS:
            return text.lower()

        return text

    @staticmethod
    def _normalize_date(value: str) -> str | None:
        if len(value) == YEAR_LENGTH and value.isdigit():
            return value

        if len(value) == YEAR_MONTH_LENGTH and value[YEAR_LENGTH] in {"-", "/"}:
            year, month = value.split(value[YEAR_LENGTH], maxsplit=1)
            if year.isdigit() and month.isdigit() and 1 <= int(month) <= MAX_MONTH_VALUE:
                return f"{year}-{int(month):02d}"

        for fmt in DATE_INPUT_FORMATS:
            try:
                parsed = datetime.strptime(value, fmt).replace(tzinfo=UTC)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    @staticmethod
    def _normalize_number(value: str) -> str | None:
        compact = value.replace(",", "").replace(" ", "")
        compact = compact.removesuffix("%")

        try:
            number = float(compact)
        except ValueError:
            return None

        if number.is_integer():
            return str(int(number))
        return str(number)

    @staticmethod
    def _dedupe(values: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for value in values:
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(value)
        return deduped
