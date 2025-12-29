from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, EmailStr
from .base import BaseEntity


class EmailAddress(BaseEntity):
    email: str = Field(..., description="Email address")
    associated_domains: List[str] = Field(default_factory=list, description="Associated domain names")
    description: Optional[str] = Field(None, description="Additional description")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.lower().strip()
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "associated_domains": ["example.com"],
                "description": "Suspicious email",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {}
            }
        }


class EmailAddressCreate(BaseModel):
    email: str
    associated_domains: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class EmailAddressUpdate(BaseModel):
    email: Optional[str] = None
    associated_domains: Optional[List[str]] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

