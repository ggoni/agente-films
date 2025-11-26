"""Unit tests for configuration module."""

import pytest
from backend.app.config import Settings


def test_settings_loads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that settings load from environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    settings = Settings()
    assert settings.DATABASE_URL == "postgresql://test"


def test_settings_has_defaults() -> None:
    """Test that settings have correct default values."""
    settings = Settings()
    assert settings.DEBUG is False
    assert settings.APP_NAME == "Film Concept Generator"


def test_settings_debug_can_be_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that DEBUG mode can be enabled via env var."""
    monkeypatch.setenv("DEBUG", "true")
    settings = Settings()
    assert settings.DEBUG is True


def test_database_url_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that database URL validation works."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/filmdb")
    settings = Settings()
    assert "postgresql" in settings.DATABASE_URL
