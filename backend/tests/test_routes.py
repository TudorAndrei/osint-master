"""API route registration tests."""

from app.main import app


def test_core_api_routes_registered() -> None:
    """Ensure key Phase 1 routes are mounted."""
    paths = {getattr(route, "path", "") for route in app.routes}

    assert "/api/investigations" in paths
    assert "/api/investigations/{investigation_id}" in paths
    assert "/api/investigations/{investigation_id}/entities" in paths
    assert "/api/investigations/{investigation_id}/entities/deduplicate/candidates" in paths
    assert "/api/investigations/{investigation_id}/entities/merge" in paths
    assert "/api/investigations/{investigation_id}/entities/{entity_id}" in paths
    assert "/api/investigations/{investigation_id}/entities/{entity_id}/expand" in paths
    assert "/api/investigations/{investigation_id}/ingest" in paths
    assert "/api/investigations/{investigation_id}/ingest/{workflow_id}/status" in paths
    assert "/api/investigations/{investigation_id}/graph" in paths
    assert "/api/investigations/{investigation_id}/notebook" in paths
    assert "/api/schema" in paths
    assert "/api/schema/{schema_name}" in paths
    assert "/api/auth/me" in paths
