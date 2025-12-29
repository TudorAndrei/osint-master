from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from .base import BaseEntity


class Person(BaseEntity):
    name: str = Field(..., min_length=1, description="Full name of the person")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or aliases")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    nationality: Optional[str] = Field(None, description="Nationality")
    description: Optional[str] = Field(None, description="Additional description")

    class Config:
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
                "metadata": {}
            }
        }


class PersonCreate(BaseModel):
    name: str = Field(..., min_length=1)
    aliases: List[str] = Field(default_factory=list)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    aliases: Optional[List[str]] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

