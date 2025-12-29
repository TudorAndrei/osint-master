from pydantic import Field

from .base import EntityMixin


class SocialMediaProfile(EntityMixin):
    platform: str = Field(..., min_length=1, description="Social media platform name")
    username: str = Field(..., min_length=1, description="Username or handle")
    profile_url: str | None = Field(None, description="Profile URL")
    display_name: str | None = Field(None, description="Display name")
    description: str | None = Field(None, description="Additional description")
