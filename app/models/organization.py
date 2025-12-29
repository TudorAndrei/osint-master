from pydantic import BaseModel, Field

from .base import BaseEntity


class Organization(BaseEntity):
    name: str = Field(..., min_length=1, description="Organization name")
    aliases: list[str] = Field(default_factory=list, description="Alternative names")
    org_type: str | None = Field(None, description="Type of organization")
    registration_number: str | None = Field(None, description="Registration or tax ID")
    country: str | None = Field(None, description="Country of registration")
    description: str | None = Field(None, description="Additional description")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Acme Corp",
                "aliases": ["ACME"],
                "org_type": "Corporation",
                "registration_number": "123456789",
                "country": "US",
                "description": "Technology company",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class OrganizationCreate(BaseModel):
    """Create model for Organization entity."""

    name: str = Field(..., min_length=1)
    aliases: list[str] = Field(default_factory=list)
    org_type: str | None = None
    registration_number: str | None = None
    country: str | None = None
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class OrganizationUpdate(BaseModel):
    """Update model for Organization entity."""

    name: str | None = Field(None, min_length=1)
    aliases: list[str] | None = None
    org_type: str | None = None
    registration_number: str | None = None
    country: str | None = None
    description: str | None = None
    metadata: dict | None = None
