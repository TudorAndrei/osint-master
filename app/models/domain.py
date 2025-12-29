from datetime import date

from pydantic import Field, field_validator

from .base import EntityMixin


class Domain(EntityMixin):
    domain_name: str = Field(..., description="Domain name")
    registration_date: date | None = Field(None, description="Registration date")
    registrar: str | None = Field(None, description="Domain registrar")
    expiration_date: date | None = Field(None, description="Expiration date")
    description: str | None = Field(None, description="Additional description")

    @field_validator("domain_name")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v = v.lower().strip()
        if not v:
            msg = "Domain name cannot be empty"
            raise ValueError(msg)
        return v
