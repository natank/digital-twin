"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/backend/src/settings.py → monorepo root (four levels up)
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _REPO_ROOT / ".env.local"


class Settings(BaseSettings):
    """Environment-driven configuration for the backend application.

    Loads from the monorepo-root ``.env.local`` (when present) and from
    process environment variables. Process env always wins over the file.
    """

    model_config = SettingsConfigDict(
        # Path may not exist yet; pydantic-settings ignores a missing file.
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+psycopg://postgres:devpassword@localhost:5432/digital_twin_dev"
    )
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = "dev-secret-only-for-testing"
    jwt_expiry: int = 86400
    debug: bool = True
    log_level: str = "DEBUG"
    claude_api_key: str = "sk-test"
    pushover_app_token: str = "test-token"
    encryption_key: str = ""
    s3_bucket: str = "digital-twin-dev"
    aws_endpoint_url: str = "http://localhost:4566"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
