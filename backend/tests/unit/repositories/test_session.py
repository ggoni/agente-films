"""Unit tests for Session repository."""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session as DBSession

from backend.app.db.repositories.session import SessionRepository
from backend.app.db.schemas import SessionCreate


def test_create_session(db_session: DBSession) -> None:
    """Test creating a new session in the repository."""
    repo = SessionRepository(db_session)
    data = SessionCreate(status="active")
    session = repo.create(data)

    assert session.id is not None
    assert session.status == "active"
    assert session.created_at is not None
    assert session.updated_at is not None


def test_create_session_with_metadata(db_session: DBSession) -> None:
    """Test creating a session with metadata."""
    repo = SessionRepository(db_session)
    metadata = {"user_id": "123", "source": "web"}
    data = SessionCreate(status="active", session_metadata=metadata)
    session = repo.create(data)

    assert session.session_metadata == metadata


def test_get_by_id_returns_session(db_session: DBSession) -> None:
    """Test retrieving a session by ID."""
    repo = SessionRepository(db_session)
    created = repo.create(SessionCreate(status="active"))
    found = repo.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.status == created.status


def test_get_by_id_returns_none_for_nonexistent(db_session: DBSession) -> None:
    """Test that get_by_id returns None for non-existent ID."""
    repo = SessionRepository(db_session)
    non_existent_id = uuid4()
    found = repo.get_by_id(non_existent_id)

    assert found is None


def test_delete_removes_session(db_session: DBSession) -> None:
    """Test deleting a session."""
    repo = SessionRepository(db_session)
    created = repo.create(SessionCreate(status="active"))

    result = repo.delete(created.id)
    assert result is True

    found = repo.get_by_id(created.id)
    assert found is None


def test_delete_returns_false_for_nonexistent(db_session: DBSession) -> None:
    """Test that delete returns False for non-existent ID."""
    repo = SessionRepository(db_session)
    non_existent_id = uuid4()
    result = repo.delete(non_existent_id)

    assert result is False


def test_repository_uses_injected_session(db_session: DBSession) -> None:
    """Test that repository uses the injected database session."""
    repo = SessionRepository(db_session)
    assert repo.db is db_session
