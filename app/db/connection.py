from typing import Optional
from redis import Redis
from falkordb import Graph
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    falkordb_host: str = "localhost"
    falkordb_port: int = 6379
    falkordb_password: Optional[str] = None
    graph_name: str = "osint"

    class Config:
        env_file = ".env"


settings = Settings()
_redis_client: Optional[Redis] = None
_graph: Optional[Graph] = None


def get_db() -> Graph:
    global _graph, _redis_client
    if _graph is None:
        _redis_client = Redis(
            host=settings.falkordb_host,
            port=settings.falkordb_port,
            password=settings.falkordb_password,
            decode_responses=True
        )
        _graph = Graph(_redis_client, settings.graph_name)
    return _graph


def close_db():
    global _graph, _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        _graph = None

