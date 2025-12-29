from pydantic import Field

from .base import EntityMixin


class Document(EntityMixin):
    title: str = Field(..., min_length=1, description="Document title")
    doc_type: str | None = Field(None, description="Document type")
    file_path: str | None = Field(None, description="Local file path")
    url: str | None = Field(None, description="Document URL")
    content_hash: str | None = Field(None, description="Content hash (SHA256)")
    description: str | None = Field(None, description="Additional description")
