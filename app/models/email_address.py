from pydantic import BaseModel, Field, field_validator

from .base import BaseEntity


class EmailAddress(BaseEntity):
    email: str = Field(..., description="Email address")
    associated_domains: list[str] = Field(
        default_factory=list, description="Associated domain names",
    )
    description: str | None = Field(None, description="Additional description")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email address."""
        v = v.lower().strip()
        if "@" not in v:
            msg = "Invalid email format"
            raise ValueError(msg)
        return v

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "associated_domains": ["example.com"],
                "description": "Suspicious email",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class EmailAddressCreate(BaseModel):
    """Create model for EmailAddress entity."""

    email: str
    associated_domains: list[str] = Field(default_factory=list)
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class EmailAddressUpdate(BaseModel):
    """Update model for EmailAddress entity."""

    email: str | None = None
    associated_domains: list[str] | None = None
    description: str | None = None
    metadata: dict | None = None
