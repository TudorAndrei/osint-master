from datetime import date

from pydantic import BaseModel, Field

from .base import BaseEntity


class Person(BaseEntity):
    name: str = Field(..., min_length=1, description="Full name of the person")
    aliases: list[str] = Field(
        default_factory=list, description="Alternative names or aliases",
    )
    date_of_birth: date | None = Field(None, description="Date of birth")
    nationality: str | None = Field(None, description="Nationality")
    description: str | None = Field(None, description="Additional description")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "aliases": ["JD", "Johnny"],
                "date_of_birth": "1990-01-01",
                "nationality": "US",
                "description": "Person of interest",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class PersonCreate(BaseModel):
    """Create model for Person entity."""

    name: str = Field(..., min_length=1)
    aliases: list[str] = Field(default_factory=list)
    date_of_birth: date | None = None
    nationality: str | None = None
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class PersonUpdate(BaseModel):
    """Update model for Person entity."""

    name: str | None = Field(None, min_length=1)
    aliases: list[str] | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    description: str | None = None
    metadata: dict | None = None
