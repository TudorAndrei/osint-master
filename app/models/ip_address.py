import ipaddress

from pydantic import Field, field_validator

from .base import EntityMixin


class IPAddress(EntityMixin):
    ip_address: str = Field(..., description="IP address (IPv4 or IPv6)")
    country: str | None = Field(None, description="Country code")
    city: str | None = Field(None, description="City")
    isp: str | None = Field(None, description="Internet Service Provider")
    description: str | None = Field(None, description="Additional description")

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        try:
            ipaddress.ip_address(v)
        except ValueError as e:
            msg = f"Invalid IP address format: {v}"
            raise ValueError(msg) from e
        else:
            return v
