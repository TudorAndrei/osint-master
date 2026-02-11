"""Schema response models."""

from pydantic import BaseModel


class SchemaProperty(BaseModel):
    """Property details for an FTM schema."""

    name: str
    label: str
    type: str
    multiple: bool


class Schema(BaseModel):
    """Basic schema description."""

    name: str
    label: str
    plural: str
    abstract: bool
    matchable: bool


class SchemaDetail(Schema):
    """Schema details including available properties."""

    properties: list[SchemaProperty]
