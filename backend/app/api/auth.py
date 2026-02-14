"""Authentication dependencies and helpers."""

from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated, Any

import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    """Information extracted from a validated Clerk token."""

    user_id: str
    session_id: str | None
    claims: dict[str, Any]


@lru_cache
def get_clerk_client() -> Clerk:
    """Build a singleton Clerk client."""
    return Clerk(bearer_auth=settings.clerk_secret_key)


def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthContext:
    """Verify incoming bearer token and return auth context."""
    if settings.auth_disabled or (settings.debug and not settings.clerk_secret_key):
        return AuthContext(
            user_id="dev-user",
            session_id=None,
            claims={"dev_mode": True},
        )

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if not settings.clerk_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication is not configured",
        )

    token = credentials.credentials
    request = httpx.Request(
        "GET", "http://local.clerk.verify", headers={"Authorization": f"Bearer {token}"}
    )

    request_state = get_clerk_client().authenticate_request(
        request,
        AuthenticateRequestOptions(
            authorized_parties=settings.clerk_authorized_parties,
        ),
    )

    if not request_state.is_signed_in or request_state.payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    payload = dict(request_state.payload)
    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    session_id = payload.get("sid")
    return AuthContext(
        user_id=user_id,
        session_id=session_id if isinstance(session_id, str) else None,
        claims=payload,
    )
