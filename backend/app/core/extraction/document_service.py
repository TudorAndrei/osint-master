"""Document parsing with Kreuzberg."""

from __future__ import annotations

from pathlib import Path

try:
    from kreuzberg import extract_bytes_sync
except ImportError:  # pragma: no cover - dependency/runtime concern
    extract_bytes_sync = None


class DocumentService:
    """Extract plain text and metadata from raw files."""

    def extract(self, content: bytes, filename: str, content_type: str | None) -> dict[str, object]:
        """Extract document content and metadata using Kreuzberg."""
        if extract_bytes_sync is None:
            msg = "kreuzberg is not installed"
            raise RuntimeError(msg)

        mime_type = content_type or self._guess_mime_type(filename)
        result = extract_bytes_sync(content, mime_type)
        metadata = dict(result.metadata) if result.metadata is not None else {}

        return {
            "content": result.content,
            "mime_type": result.mime_type,
            "metadata": metadata,
            "document_type": self.detect_document_type(filename, result.content, metadata),
        }

    @staticmethod
    def _guess_mime_type(filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            return "application/pdf"
        if suffix in {".html", ".htm"}:
            return "text/html"
        if suffix == ".eml":
            return "message/rfc822"
        if suffix == ".msg":
            return "application/vnd.ms-outlook"
        if suffix == ".txt":
            return "text/plain"
        return "application/octet-stream"

    @staticmethod
    def detect_document_type(filename: str, content: str, metadata: dict) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix in {".eml", ".msg"} or metadata.get("format_type") == "email":
            return "email"

        upper_text = (content or "")[:10000].upper()
        if "FORM 10-K" in upper_text or "FORM 10-Q" in upper_text or "FORM 8-K" in upper_text:
            return "sec_filing"

        return "general"
