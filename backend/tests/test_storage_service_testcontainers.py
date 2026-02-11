"""Integration tests for S3 storage behavior using Testcontainers."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest

from app.config import settings
from app.core.storage_service import StorageService

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_TESTCONTAINERS") != "1",
    reason="Set RUN_TESTCONTAINERS=1 to run container-based integration tests",
)


@pytest.fixture
def minio_endpoint() -> Generator[str, None, None]:
    """Provide a temporary S3-compatible endpoint via Testcontainers."""
    testcontainers = pytest.importorskip("testcontainers")
    _ = testcontainers
    from testcontainers.core.container import DockerContainer  # type: ignore[import-not-found]

    container = DockerContainer("minio/minio:latest")
    container = container.with_env("MINIO_ROOT_USER", "minioadmin")
    container = container.with_env("MINIO_ROOT_PASSWORD", "minioadmin")
    container = container.with_command("server /data --console-address :9001")
    container = container.with_exposed_ports(9000)

    with container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(9000)
        yield f"http://{host}:{port}"


def _configure_storage(endpoint: str) -> StorageService:
    settings.s3_endpoint_url = endpoint
    settings.s3_access_key = "minioadmin"
    settings.s3_secret_key = "minioadmin"
    settings.s3_region = "us-east-1"
    settings.s3_secure = False
    settings.s3_bucket_name = "documents"
    return StorageService()


def test_upload_and_download_isolated_by_investigation_bucket(minio_endpoint: str) -> None:
    """Same object key in different investigations must not collide."""
    storage = _configure_storage(minio_endpoint)

    investigation_a = "inv-a-11111111-1111-1111-1111-111111111111"
    investigation_b = "inv-b-22222222-2222-2222-2222-222222222222"
    doc_id = "doc-123"
    filename = "report.pdf"

    key_a = storage.upload_bytes(investigation_a, doc_id, filename, b"alpha", "application/pdf")
    key_b = storage.upload_bytes(investigation_b, doc_id, filename, b"beta", "application/pdf")

    assert key_a == key_b
    assert storage.download_bytes(investigation_a, key_a) == b"alpha"
    assert storage.download_bytes(investigation_b, key_b) == b"beta"


def test_object_url_uses_per_investigation_bucket(minio_endpoint: str) -> None:
    """Object URL should resolve to a bucket derived from investigation id."""
    storage = _configure_storage(minio_endpoint)

    investigation = "be17fbf3-6404-46c2-ab24-27b5d1b7ec53"
    key = "doc-777/file.txt"
    url = storage.object_url(investigation, key)

    assert url.startswith("s3://documents-")
    assert url.endswith("/doc-777/file.txt")
