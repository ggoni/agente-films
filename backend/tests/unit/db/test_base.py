"""Unit tests for database base module."""

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from backend.app.db.base import Base, get_engine, get_session


def test_get_engine_returns_engine() -> None:
    """Test that get_engine returns a SQLAlchemy Engine."""
    engine = get_engine()
    assert isinstance(engine, Engine)


def test_get_engine_is_singleton() -> None:
    """Test that get_engine returns the same instance."""
    engine1 = get_engine()
    engine2 = get_engine()
    assert engine1 is engine2


def test_get_session_yields_session() -> None:
    """Test that get_session yields a SQLAlchemy Session."""
    gen = get_session()
    session = next(gen)
    assert isinstance(session, Session)
    gen.close()


def test_base_exists() -> None:
    """Test that Base declarative base exists."""
    assert Base is not None
    assert hasattr(Base, "metadata")


def test_engine_has_pooling_config() -> None:
    """Test that engine is configured with connection pooling."""
    engine = get_engine()
    assert engine.pool.size() >= 0  # Pool exists
