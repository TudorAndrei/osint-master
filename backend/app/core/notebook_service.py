"""Notebook persistence service backed by PostgreSQL."""

from __future__ import annotations

from datetime import UTC, datetime
from threading import Lock
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import settings
from app.models.notebook import NotebookCanvas, NotebookDocument


class NotebookConflictError(RuntimeError):
    """Raised when a notebook update conflicts with a newer version."""


class NotebookService:
    """Persist and retrieve investigation notebooks."""

    _init_lock = Lock()
    _initialized = False
    _create_error_message = "Unable to create notebook"
    _conflict_error_message = "Notebook version conflict"

    def __init__(self) -> None:
        configured_url = settings.notebook_database_url or settings.dbos_system_database_url
        self.database_url = configured_url
        self._ensure_schema()

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url)

    def _ensure_schema(self) -> None:
        if NotebookService._initialized:
            return
        with NotebookService._init_lock:
            if NotebookService._initialized:
                return
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS investigation_notebooks (
                            id UUID PRIMARY KEY,
                            investigation_id TEXT NOT NULL UNIQUE,
                            canvas_doc JSONB NOT NULL,
                            version INTEGER NOT NULL DEFAULT 1,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                        )
                        """
                    )
                conn.commit()
            NotebookService._initialized = True

    def _default_canvas(self) -> dict[str, Any]:
        return NotebookCanvas().model_dump(mode="json")

    def _create_default(self, investigation_id: str) -> NotebookDocument:
        now = datetime.now(UTC)
        payload = {
            "id": str(uuid4()),
            "investigation_id": investigation_id,
            "canvas_doc": self._default_canvas(),
            "version": 1,
            "created_at": now,
            "updated_at": now,
        }

        with self._connect() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO investigation_notebooks (
                    id,
                    investigation_id,
                    canvas_doc,
                    version,
                    created_at,
                    updated_at
                ) VALUES (
                    %(id)s,
                    %(investigation_id)s,
                    %(canvas_doc)s::jsonb,
                    %(version)s,
                    %(created_at)s,
                    %(updated_at)s
                )
                ON CONFLICT (investigation_id) DO NOTHING
                """,
                {
                    **payload,
                    "canvas_doc": Jsonb(payload["canvas_doc"]),
                },
            )
            cur.execute(
                """
                SELECT investigation_id, canvas_doc, version, created_at, updated_at
                FROM investigation_notebooks
                WHERE investigation_id = %(investigation_id)s
                """,
                {"investigation_id": investigation_id},
            )
            row = cur.fetchone()
        if row is None:
            raise RuntimeError(self._create_error_message)
        return self._row_to_document(row)

    def _row_to_document(self, row: dict[str, Any]) -> NotebookDocument:
        return NotebookDocument(
            investigation_id=row["investigation_id"],
            version=int(row["version"]),
            canvas_doc=NotebookCanvas.model_validate(row["canvas_doc"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_or_create(self, investigation_id: str) -> NotebookDocument:
        """Fetch notebook for investigation, creating an empty one if absent."""
        with self._connect() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT investigation_id, canvas_doc, version, created_at, updated_at
                FROM investigation_notebooks
                WHERE investigation_id = %(investigation_id)s
                """,
                {"investigation_id": investigation_id},
            )
            row = cur.fetchone()

        if row is not None:
            return self._row_to_document(row)
        return self._create_default(investigation_id)

    def save(
        self,
        investigation_id: str,
        version: int,
        canvas_doc: NotebookCanvas,
    ) -> NotebookDocument:
        """Save notebook document using optimistic concurrency."""
        with self._connect() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    UPDATE investigation_notebooks
                    SET canvas_doc = %(canvas_doc)s::jsonb,
                        version = version + 1,
                        updated_at = NOW()
                    WHERE investigation_id = %(investigation_id)s
                      AND version = %(version)s
                    RETURNING investigation_id, canvas_doc, version, created_at, updated_at
                    """,
                    {
                        "investigation_id": investigation_id,
                        "version": version,
                        "canvas_doc": Jsonb(canvas_doc.model_dump(mode="json")),
                    },
                )
                row = cur.fetchone()

            if row is not None:
                conn.commit()
                return self._row_to_document(row)

            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT investigation_id, canvas_doc, version, created_at, updated_at
                    FROM investigation_notebooks
                    WHERE investigation_id = %(investigation_id)s
                    """,
                    {"investigation_id": investigation_id},
                )
                existing = cur.fetchone()

        if existing is None:
            created = self._create_default(investigation_id)
            if created.version != version:
                raise NotebookConflictError(self._conflict_error_message)
            return self.save(investigation_id, version, canvas_doc)

        raise NotebookConflictError(self._conflict_error_message)
