"""Unit tests for database models."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import inspect

from backend.app.db.models import Session


def test_session_model_has_required_fields() -> None:
    """Test that Session model has all required fields."""
    session_id = uuid4()
    session = Session(
        id=session_id,
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    assert session.id == session_id
    assert session.status == "active"
    assert isinstance(session.created_at, datetime)
    assert isinstance(session.updated_at, datetime)


def test_session_model_column_defaults() -> None:
    """Test that Session model columns have correct default configurations."""
    mapper = inspect(Session)

    # Check status has default
    status_col = mapper.columns["status"]
    assert status_col.default is not None
    assert status_col.default.arg == "active"

    # Check timestamps have defaults
    created_at_col = mapper.columns["created_at"]
    updated_at_col = mapper.columns["updated_at"]
    assert created_at_col.default is not None
    assert updated_at_col.default is not None


def test_session_with_metadata() -> None:
    """Test that Session model can store metadata as JSON."""
    session_id = uuid4()
    metadata = {"user_id": "123", "source": "web"}
    now = datetime.now(UTC)
    session = Session(
        id=session_id,
        status="active",
        session_metadata=metadata,
        created_at=now,
        updated_at=now,
    )

    assert session.session_metadata == metadata
    assert session.session_metadata["user_id"] == "123"


def test_session_status_values() -> None:
    """Test that Session model accepts different status values."""
    now = datetime.now(UTC)
    for status in ["active", "completed", "failed", "cancelled"]:
        session = Session(id=uuid4(), status=status, created_at=now, updated_at=now)
        assert session.status == status


def test_session_table_name() -> None:
    """Test that Session model has correct table name."""
    assert Session.__tablename__ == "sessions"


def test_session_primary_key() -> None:
    """Test that Session model has UUID primary key."""
    mapper = inspect(Session)
    pk_columns = [col.name for col in mapper.primary_key]
    assert "id" in pk_columns
    assert len(pk_columns) == 1
