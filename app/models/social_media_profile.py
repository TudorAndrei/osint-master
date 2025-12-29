from pydantic import BaseModel, Field

from .base import BaseEntity


class SocialMediaProfile(BaseEntity):
    platform: str = Field(..., min_length=1, description="Social media platform name")
    username: str = Field(..., min_length=1, description="Username or handle")
    profile_url: str | None = Field(None, description="Profile URL")
    display_name: str | None = Field(None, description="Display name")
    description: str | None = Field(None, description="Additional description")

    class Config:
        """Pydantic configuration."""

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
                "metadata": {},
            },
        }


class SocialMediaProfileCreate(BaseModel):
    """Create model for SocialMediaProfile entity."""

    platform: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    profile_url: str | None = None
    display_name: str | None = None
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class SocialMediaProfileUpdate(BaseModel):
    """Update model for SocialMediaProfile entity."""

    platform: str | None = Field(None, min_length=1)
    username: str | None = Field(None, min_length=1)
    profile_url: str | None = None
    display_name: str | None = None
    description: str | None = None
    metadata: dict | None = None
