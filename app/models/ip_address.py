import ipaddress

from pydantic import BaseModel, Field, field_validator

from .base import BaseEntity


class IPAddress(BaseEntity):
    ip_address: str = Field(..., description="IP address (IPv4 or IPv6)")
    country: str | None = Field(None, description="Country code")
    city: str | None = Field(None, description="City")
    isp: str | None = Field(None, description="Internet Service Provider")
    description: str | None = Field(None, description="Additional description")

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            msg = f"Invalid IP address format: {v}"
            raise ValueError(msg)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "ip_address": "192.168.1.1",
                "country": "US",
                "city": "New York",
                "isp": "Example ISP",
                "description": "Suspicious IP",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "metadata": {},
            },
        }


class IPAddressCreate(BaseModel):
    """Create model for IPAddress entity."""

    ip_address: str
    country: str | None = None
    city: str | None = None
    isp: str | None = None
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class IPAddressUpdate(BaseModel):
    """Update model for IPAddress entity."""

    ip_address: str | None = None
    country: str | None = None
    city: str | None = None
    isp: str | None = None
    description: str | None = None
    metadata: dict | None = None
