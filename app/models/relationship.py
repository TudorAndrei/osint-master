from pydantic import Field, model_validator

from .base import EntityMixin


class Relationship(EntityMixin):
    source_entity_id: str = Field(..., description="Source entity ID")
    target_entity_id: str = Field(..., description="Target entity ID")
    relationship_type: str = Field(
        ...,
        min_length=1,
        description="Type of relationship",
    )
    description: str | None = Field(None, description="Relationship description")

    @model_validator(mode="after")
    def validate_not_self_referential(self) -> "Relationship":
        if (
            self.source_entity_id is not None
            and self.target_entity_id is not None
            and self.source_entity_id == self.target_entity_id
        ):
            msg = "Source and target entity IDs cannot be the same"
            raise ValueError(msg)
        return self
