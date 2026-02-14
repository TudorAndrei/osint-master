"""Authentication route and dependency behavior."""

from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from app.api.auth import AuthContext, require_auth
from app.main import app

client = TestClient(app)


@dataclass
class FakeRequestState:
    """Minimal Clerk request-state shape for tests."""

    is_signed_in: bool
    payload: dict[str, Any] | None


class FakeClerkClient:
    """Fake Clerk client for invalid-token test."""

    def __init__(self, request_state: FakeRequestState) -> None:
        self.request_state = request_state

    def authenticate_request(self, *_: object, **__: object) -> FakeRequestState:
        return self.request_state


def test_auth_me_requires_token() -> None:
    """No Authorization header should return 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_auth_me_rejects_invalid_token(monkeypatch: Any) -> None:
    """Invalid token should return 401."""
    monkeypatch.setattr("app.api.auth.settings.clerk_secret_key", "sk_test")
    fake_client = FakeClerkClient(FakeRequestState(is_signed_in=False, payload=None))
    monkeypatch.setattr("app.api.auth.get_clerk_client", lambda: fake_client)

    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_auth_me_returns_context_with_valid_auth_override() -> None:
    """Valid auth dependency should expose user context."""
    app.dependency_overrides[require_auth] = lambda: AuthContext(
        user_id="user_123",
        session_id="sess_123",
        claims={"sub": "user_123", "sid": "sess_123"},
    )
    try:
        response = client.get("/api/auth/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == "user_123"
    assert payload["session_id"] == "sess_123"
    assert payload["claims"]["sub"] == "user_123"
