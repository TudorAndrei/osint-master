from falkordb import Graph
from pydantic_settings import BaseSettings
from redis import ConnectionPool, Redis


class Settings(BaseSettings):
    falkordb_host: str = "localhost"
    falkordb_port: int = 6379
    falkordb_password: str | None = None
    graph_name: str = "osint"
    connection_pool_size: int = 50

    class Config:
        env_file = ".env"


settings = Settings()


class ConnectionPoolManager:
    def __init__(self) -> None:
        self._pool: ConnectionPool | None = None

    def init(self) -> None:
        if self._pool is None:
            self._pool = ConnectionPool(
                host=settings.falkordb_host,
                port=settings.falkordb_port,
                password=settings.falkordb_password,
                decode_responses=True,
                max_connections=settings.connection_pool_size,
            )

    def close(self) -> None:
        if self._pool:
            self._pool.disconnect()
            self._pool = None

    def get_db(self) -> Graph:
        if self._pool is None:
            msg = "Connection pool not initialized. Call init_connection_pool() first."
            raise RuntimeError(msg)
        redis_client = Redis(connection_pool=self._pool)
        return Graph(redis_client, settings.graph_name)


_pool_manager = ConnectionPoolManager()


def init_connection_pool() -> None:
    _pool_manager.init()


def close_connection_pool() -> None:
    _pool_manager.close()


def get_db() -> Graph:
    return _pool_manager.get_db()
