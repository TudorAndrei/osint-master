from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from .base import BaseEntity


class SocialMediaProfile(BaseEntity):
    platform: str = Field(..., min_length=1, description="Social media platform name")
    username: str = Field(..., min_length=1, description="Username or handle")
    profile_url: Optional[str] = Field(None, description="Profile URL")
    display_name: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Additional description")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "platform": "Twitter",
                "username": "@example",
                "profile_url": "https://twitter.com/example",
                "display_name": "Example User",
                "description": "Suspicious profile",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {}
            }
        }


class SocialMediaProfileCreate(BaseModel):
    platform: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    profile_url: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class SocialMediaProfileUpdate(BaseModel):
    platform: Optional[str] = Field(None, min_length=1)
    username: Optional[str] = Field(None, min_length=1)
    profile_url: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

