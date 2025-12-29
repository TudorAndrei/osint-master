from collections.abc import Iterator

import pytest
from falkordb import Graph
from fastapi.testclient import TestClient
from redis import Redis
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from app.db.connection import close_connection_pool, get_db, init_connection_pool, settings
from app.main import app


@pytest.fixture(scope="session")
def falkordb_container() -> Iterator[DockerContainer]:
    container = (
        DockerContainer("falkordb/falkordb:latest")
        .with_exposed_ports(6379)
        .with_env("FALKORDB_PASSWORD", "")
    )
    container.start()
    wait_for_logs(container, "Ready to accept connections", timeout=30)
    yield container
    container.stop()


@pytest.fixture(scope="session")
def test_db(falkordb_container: DockerContainer) -> Iterator[Graph]:
    host = falkordb_container.get_container_host_ip()
    port = falkordb_container.get_exposed_port(6379)

    redis_client = Redis(
        host=host,
        port=port,
        password=None,
        decode_responses=True,
    )
    graph = Graph(redis_client, "test_osint")

    yield graph

    redis_client.close()


@pytest.fixture(scope="session")
def test_db_settings(
    falkordb_container: DockerContainer,
) -> dict[str, str | int | None]:
    host = falkordb_container.get_container_host_ip()
    port = falkordb_container.get_exposed_port(6379)
    return {
        "falkordb_host": host,
        "falkordb_port": port,
        "falkordb_password": None,
        "graph_name": "test_osint",
    }


@pytest.fixture(autouse=True)
def setup_test_db(
    test_db_settings: dict[str, str | int | None],
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    monkeypatch.setenv("FALKORDB_HOST", test_db_settings["falkordb_host"])
    monkeypatch.setenv("FALKORDB_PORT", str(test_db_settings["falkordb_port"]))
    monkeypatch.setenv(
        "FALKORDB_PASSWORD",
        str(test_db_settings["falkordb_password"] or ""),
    )
    monkeypatch.setenv("GRAPH_NAME", test_db_settings["graph_name"])

    close_connection_pool()

    monkeypatch.setattr(settings, "falkordb_host", test_db_settings["falkordb_host"])
    monkeypatch.setattr(settings, "falkordb_port", test_db_settings["falkordb_port"])
    monkeypatch.setattr(
        settings,
        "falkordb_password",
        test_db_settings["falkordb_password"],
    )
    monkeypatch.setattr(settings, "graph_name", test_db_settings["graph_name"])

    yield

    close_connection_pool()


@pytest.fixture
def client(test_db: Graph, setup_test_db: None) -> TestClient:
    close_connection_pool()
    init_connection_pool()

    def override_get_db() -> Graph:
        return test_db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    close_connection_pool()
