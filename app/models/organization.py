from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseEntity


class Organization(BaseEntity):
    name: str = Field(..., min_length=1, description="Organization name")
    aliases: List[str] = Field(default_factory=list, description="Alternative names")
    org_type: Optional[str] = Field(None, description="Type of organization")
    registration_number: Optional[str] = Field(None, description="Registration or tax ID")
    country: Optional[str] = Field(None, description="Country of registration")
    description: Optional[str] = Field(None, description="Additional description")

    class Config:
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
                "metadata": {}
            }
        }


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1)
    aliases: List[str] = Field(default_factory=list)
    org_type: Optional[str] = None
    registration_number: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    aliases: Optional[List[str]] = None
    org_type: Optional[str] = None
    registration_number: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

