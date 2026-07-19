"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
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

    # Database & cache
    database_url: str = "postgresql+psycopg://postgres:devpassword@localhost:5432/digital_twin_dev"
    redis_url: str = "redis://localhost:6379"

    # Auth / JWT
    # >= 32 bytes recommended for HS256 (RFC 7518).
    jwt_secret: str = "dev-secret-only-for-testing-min-32b"
    jwt_expiry: int = 86400
    jwt_algorithm: str = "HS256"
    auth_login_max_attempts: int = 5
    auth_login_lockout_seconds: int = 900
    # When False (default for production-minded deploys), login requires
    # email_verified. Dev defaults to True so local smoke tests work before
    # the verification flow (PR-004) is complete.
    auth_allow_unverified_login: bool = True

    # App
    debug: bool = True
    log_level: str = "DEBUG"
    cors_origins: str = Field(
        default="http://localhost:4200,http://127.0.0.1:4200",
        description="Comma-separated browser origins allowed by CORS",
    )

    # Email (console backend until a real provider is wired)
    email_backend: str = "console"
    email_from: str = "noreply@localhost"

    # OAuth placeholders
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    github_oauth_client_id: str = ""
    github_oauth_client_secret: str = ""

    # LLM / notifications / storage placeholders
    claude_api_key: str = "sk-test"
    claude_model: str = "claude-sonnet-4-20250514"
    pushover_app_token: str = "test-token"
    encryption_key: str = ""
    s3_bucket: str = "digital-twin-dev"
    aws_endpoint_url: str = "http://localhost:4566"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_default_region: str = "us-east-1"

    # Celery (defaults reuse Redis; override for dedicated broker DBs)
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    # When True, tasks run in-process (pytest / offline). Prefer env
    # CELERY_TASK_ALWAYS_EAGER=true in CI rather than shipping True defaults.
    celery_task_always_eager: bool = False

    # Chat (visitor twin sessions)
    chat_session_ttl_minutes: int = 30
    chat_rate_limit_per_hour: int = 50
    chat_rate_limit_window_seconds: int = 3600
    chat_sse_chunk_size: int = 48

    def cors_origin_list(self) -> list[str]:
        """Parse ``cors_origins`` into a list of non-empty origin strings."""
        return [part.strip() for part in self.cors_origins.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
