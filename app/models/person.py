from datetime import date

from pydantic import Field

from .base import EntityMixin


class Person(EntityMixin):
    name: str = Field(..., min_length=1, description="Full name of the person")
    aliases: list[str] = Field(
        default_factory=list,
        description="Alternative names or aliases",
    )
    date_of_birth: date | None = Field(None, description="Date of birth")
    nationality: str | None = Field(None, description="Nationality")
    description: str | None = Field(None, description="Additional description")
