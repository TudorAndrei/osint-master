from pydantic import BaseModel, Field

from .base import BaseEntity


class Document(BaseEntity):
    title: str = Field(..., min_length=1, description="Document title")
    doc_type: str | None = Field(None, description="Document type")
    file_path: str | None = Field(None, description="Local file path")
    url: str | None = Field(None, description="Document URL")
    content_hash: str | None = Field(None, description="Content hash (SHA256)")
    description: str | None = Field(None, description="Additional description")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Report.pdf",
                "doc_type": "PDF",
                "file_path": "/data/reports/report.pdf",
                "url": "https://example.com/report.pdf",
                "content_hash": "abc123...",
                "description": "Intelligence report",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class DocumentCreate(BaseModel):
    """Create model for Document entity."""

    title: str = Field(..., min_length=1)
    doc_type: str | None = None
    file_path: str | None = None
    url: str | None = None
    content_hash: str | None = None
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    """Update model for Document entity."""

    title: str | None = Field(None, min_length=1)
    doc_type: str | None = None
    file_path: str | None = None
    url: str | None = None
    content_hash: str | None = None
    description: str | None = None
    metadata: dict | None = None
