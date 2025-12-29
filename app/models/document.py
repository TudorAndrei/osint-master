from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseEntity


class Document(BaseEntity):
    title: str = Field(..., min_length=1, description="Document title")
    doc_type: Optional[str] = Field(None, description="Document type")
    file_path: Optional[str] = Field(None, description="Local file path")
    url: Optional[str] = Field(None, description="Document URL")
    content_hash: Optional[str] = Field(None, description="Content hash (SHA256)")
    description: Optional[str] = Field(None, description="Additional description")

    class Config:
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
                "metadata": {}
            }
        }


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    doc_type: Optional[str] = None
    file_path: Optional[str] = None
    url: Optional[str] = None
    content_hash: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    doc_type: Optional[str] = None
    file_path: Optional[str] = None
    url: Optional[str] = None
    content_hash: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

