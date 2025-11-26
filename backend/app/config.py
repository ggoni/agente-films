"""Application configuration using Pydantic settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = Field(
        default="postgresql://localhost:5432/filmdb",
        description="PostgreSQL database connection URL",
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    APP_NAME: str = Field(
        default="Film Concept Generator",
        description="Application name",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
