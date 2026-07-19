"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven configuration for the backend application."""

    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:devpassword@localhost:5432/digital_twin_dev"
    redis_url: str = "redis://localhost:6379"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
