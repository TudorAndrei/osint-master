from typing import Optional
from pydantic import BaseModel, Field, field_validator
import ipaddress
from .base import BaseEntity


class IPAddress(BaseEntity):
    ip_address: str = Field(..., description="IP address (IPv4 or IPv6)")
    country: Optional[str] = Field(None, description="Country code")
    city: Optional[str] = Field(None, description="City")
    isp: Optional[str] = Field(None, description="Internet Service Provider")
    description: Optional[str] = Field(None, description="Additional description")

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address format: {v}")

    class Config:
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
                "metadata": {}
            }
        }


class IPAddressCreate(BaseModel):
    ip_address: str
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class IPAddressUpdate(BaseModel):
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

