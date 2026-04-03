from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
    )
    SECRET_KEY: str = Field(
        default="change-me-with-a-strong-32-char-secret"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    ALGORITHM: str = Field(default="HS256")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

