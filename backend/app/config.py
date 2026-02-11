"""Application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", REPO_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # FalkorDB
    falkordb_host: str = "localhost"
    falkordb_port: int = 6379
    falkordb_password: str | None = None

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Yente
    yente_url: str = "http://localhost:8001"
    yente_dataset: str = "default"
    yente_timeout_seconds: int = 15

    # RustFS / S3-compatible storage
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "rustfsadmin"
    s3_secret_key: str = "rustfsadmin"
    s3_region: str = "us-east-1"
    s3_bucket_name: str = "documents"
    s3_secure: bool = False

    # LLM extraction
    gemini_api_key: str = ""
    extract_model_id: str = "gemini-2.5-flash"

    # DBOS
    dbos_app_name: str = "osint-master-ingest"
    dbos_system_database_url: str = "postgresql://postgres:postgres@localhost:5432/osint"


settings = Settings()
