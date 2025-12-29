from pydantic import Field, field_validator

from .base import EntityMixin


class EmailAddress(EntityMixin):
    email: str = Field(..., description="Email address")
    associated_domains: list[str] = Field(
        default_factory=list,
        description="Associated domain names",
    )
    description: str | None = Field(None, description="Additional description")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.lower().strip()
        if "@" not in v:
            msg = "Invalid email format"
            raise ValueError(msg)
        return v
