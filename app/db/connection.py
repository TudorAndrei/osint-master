from falkordb import Graph
from pydantic_settings import BaseSettings
from redis import Redis


class Settings(BaseSettings):
    falkordb_host: str = "localhost"
    falkordb_port: int = 6379
    falkordb_password: str | None = None
    graph_name: str = "osint"

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"


settings = Settings()
_redis_client: Redis | None = None
_graph: Graph | None = None


def get_db() -> Graph:
    """Get the database connection."""
    global _graph, _redis_client
    if _graph is None:
        _redis_client = Redis(
            host=settings.falkordb_host,
            port=settings.falkordb_port,
            password=settings.falkordb_password,
            decode_responses=True,
        )
        _graph = Graph(_redis_client, settings.graph_name)
    return _graph


def close_db() -> None:
    """Close the database connection."""
    global _graph, _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        _graph = None
