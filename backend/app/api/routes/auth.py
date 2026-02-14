"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.auth import AuthContext, require_auth

router = APIRouter()


@router.get("/me")
async def get_current_user(
    context: Annotated[AuthContext, Depends(require_auth)],
) -> dict[str, object]:
    """Return minimal auth context for the currently authenticated user."""
    return {
        "user_id": context.user_id,
        "session_id": context.session_id,
        "claims": context.claims,
    }
