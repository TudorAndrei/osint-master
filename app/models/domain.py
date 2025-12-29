from datetime import date

from pydantic import BaseModel, Field, field_validator

from .base import BaseEntity


class Domain(BaseEntity):
    domain_name: str = Field(..., description="Domain name")
    registration_date: date | None = Field(None, description="Registration date")
    registrar: str | None = Field(None, description="Domain registrar")
    expiration_date: date | None = Field(None, description="Expiration date")
    description: str | None = Field(None, description="Additional description")

    @field_validator("domain_name")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate and normalize domain name."""
        v = v.lower().strip()
        if not v:
            msg = "Domain name cannot be empty"
            raise ValueError(msg)
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "domain_name": "example.com",
                "registration_date": "2020-01-01",
                "registrar": "Example Registrar",
                "expiration_date": "2025-01-01",
                "description": "Suspicious domain",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class DomainCreate(BaseModel):
    """Create model for Domain entity."""

    domain_name: str
    registration_date: date | None = None
    registrar: str | None = None
    expiration_date: date | None = None
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class DomainUpdate(BaseModel):
    """Update model for Domain entity."""

    domain_name: str | None = None
    registration_date: date | None = None
    registrar: str | None = None
    expiration_date: date | None = None
    description: str | None = None
    metadata: dict | None = None
