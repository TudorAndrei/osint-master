from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .base import BaseEntity


class Domain(BaseEntity):
    domain_name: str = Field(..., description="Domain name")
    registration_date: Optional[date] = Field(None, description="Registration date")
    registrar: Optional[str] = Field(None, description="Domain registrar")
    expiration_date: Optional[date] = Field(None, description="Expiration date")
    description: Optional[str] = Field(None, description="Additional description")

    @field_validator("domain_name")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v = v.lower().strip()
        if not v:
            raise ValueError("Domain name cannot be empty")
        return v

    class Config:
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
                "metadata": {}
            }
        }


class DomainCreate(BaseModel):
    domain_name: str
    registration_date: Optional[date] = None
    registrar: Optional[str] = None
    expiration_date: Optional[date] = None
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class DomainUpdate(BaseModel):
    domain_name: Optional[str] = None
    registration_date: Optional[date] = None
    registrar: Optional[str] = None
    expiration_date: Optional[date] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

