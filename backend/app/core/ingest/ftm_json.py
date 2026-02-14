"""FTM JSON/NDJSON ingestor."""

import json
from collections.abc import Callable, Iterator
from importlib import import_module
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast

from app.core.ingest.base import BaseIngestor


class FTMJsonIngestor(BaseIngestor):
    """Ingestor for FTM JSON and NDJSON (newline-delimited JSON) files."""

    @property
    def name(self) -> str:
        return "FTM JSON"

    @property
    def supported_extensions(self) -> list[str]:
        return [".ftm", ".ijson", ".json", ".ndjson"]

    def __init__(self) -> None:
        self.filename_hint: str | None = None

    def set_filename_hint(self, filename: str | None) -> None:
        self.filename_hint = filename

    def ingest(self, content: bytes) -> Iterator[dict]:
        """Parse FTM JSON/NDJSON content and yield entities.

        Supports both:
        - Single JSON array of entities
        - Newline-delimited JSON (one entity per line)
        """
        smart_read_proxies = self._smart_read_proxies()
        if smart_read_proxies is not None and self.filename_hint is not None:
            suffix = Path(self.filename_hint).suffix.lower() or ".json"
            with NamedTemporaryFile(suffix=suffix) as tmp_file:
                tmp_file.write(content)
                tmp_file.flush()
                for proxy in smart_read_proxies(tmp_file.name):
                    if (entity := self._proxy_to_dict(proxy)) is not None:
                        yield entity
            return

        text = content.decode("utf-8")

        # Try parsing as JSON array first
        stripped = text.strip()
        if stripped.startswith("["):
            entities = json.loads(stripped)
            yield from entities
            return

        # Otherwise, parse as newline-delimited JSON
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            entity = json.loads(line)
            yield entity

    @staticmethod
    def _smart_read_proxies() -> Callable[[str], Iterator[object]] | None:
        try:
            module = import_module("ftmq.io")
        except ImportError:  # pragma: no cover - optional dependency
            return None
        candidate = getattr(module, "smart_read_proxies", None)
        if callable(candidate):
            return cast("Callable[[str], Iterator[object]]", candidate)
        return None

    @staticmethod
    def _proxy_to_dict(proxy: object) -> dict[str, object] | None:
        if isinstance(proxy, dict):
            return cast("dict[str, object]", proxy)
        to_dict = getattr(proxy, "to_dict", None)
        if callable(to_dict):
            data = to_dict()
            if isinstance(data, dict):
                return cast("dict[str, object]", data)
        if hasattr(proxy, "id") and hasattr(proxy, "schema") and hasattr(proxy, "properties"):
            return {
                "id": str(getattr(proxy, "id", "")),
                "schema": str(getattr(proxy, "schema", "")),
                "properties": {
                    str(key): [str(item) for item in values]
                    for key, values in dict(getattr(proxy, "properties", {})).items()
                },
            }
        return None
