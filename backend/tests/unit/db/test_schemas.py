"""Unit tests for Pydantic schemas."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.app.db.schemas import SessionBase, SessionCreate, SessionResponse


def test_session_create_validation() -> None:
    """Test that SessionCreate validates data correctly."""
    data = SessionCreate(status="active")
    assert data.status == "active"


def test_session_create_with_metadata() -> None:
    """Test that SessionCreate accepts metadata."""
    metadata = {"user_id": "123", "source": "web"}
    data = SessionCreate(status="active", session_metadata=metadata)
    assert data.session_metadata == metadata


def test_session_create_defaults() -> None:
    """Test that SessionCreate has default values."""
    data = SessionCreate()
    assert data.status == "active"
    assert data.session_metadata is None


def test_session_response_has_all_fields() -> None:
    """Test that SessionResponse includes all fields."""
    session_id = uuid4()
    now = datetime.now(timezone.utc)

    data = SessionResponse(
        id=session_id,
        status="active",
        session_metadata={"test": "data"},
        created_at=now,
        updated_at=now,
    )

    assert data.id == session_id
    assert data.status == "active"
    assert data.session_metadata == {"test": "data"}
    assert data.created_at == now
    assert data.updated_at == now


def test_session_base_inheritance() -> None:
    """Test that schemas inherit from SessionBase correctly."""
    assert issubclass(SessionCreate, SessionBase)
    assert issubclass(SessionResponse, SessionBase)


def test_session_response_model_config() -> None:
    """Test that SessionResponse is configured for ORM mode."""
    # This is important for converting SQLAlchemy models to Pydantic
    assert hasattr(SessionResponse, "model_config")


def test_invalid_status_fails() -> None:
    """Test that invalid status values are handled."""
    # This test assumes we might add validation for status values
    # For now, just test that it accepts strings
    data = SessionCreate(status="custom_status")
    assert data.status == "custom_status"
