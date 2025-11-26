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

    # LiteLLM Configuration
    LITELLM_BASE_URL: str = Field(
        default="http://litellm-proxy:4000",
        description="LiteLLM proxy base URL",
    )
    LITELLM_API_KEY: str = Field(
        default="",
        description="LiteLLM master key for authentication",
    )
    MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Default model name from LiteLLM proxy",
    )

    # Model Provider API Keys (optional, configured in LiteLLM)
    GOOGLE_CLOUD_PROJECT: str = Field(
        default="",
        description="Google Cloud project ID for Vertex AI",
    )
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key",
    )
    ANTHROPIC_API_KEY: str = Field(
        default="",
        description="Anthropic API key",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
