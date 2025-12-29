from pydantic import Field

from .base import EntityMixin


class Organization(EntityMixin):
    name: str = Field(..., min_length=1, description="Organization name")
    aliases: list[str] = Field(default_factory=list, description="Alternative names")
    org_type: str | None = Field(None, description="Type of organization")
    registration_number: str | None = Field(None, description="Registration or tax ID")
    country: str | None = Field(None, description="Country of registration")
    description: str | None = Field(None, description="Additional description")
