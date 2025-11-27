"""Unit tests for SessionService."""

from typing import Any
from unittest.mock import Mock
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_session_service_creates_session(db_session: Any) -> None:
    """Test creating a new session."""
    from backend.app.services.session_service import SessionService

    service = SessionService(db_session)
    session_id = await service.create_session()

    assert session_id is not None
    assert isinstance(session_id, type(uuid4()))


@pytest.mark.asyncio
async def test_session_service_get_runner() -> None:
    """Test getting an ADK runner for a session."""
    from backend.app.services.session_service import SessionService

    db_session = Mock()
    service = SessionService(db_session)
    session_id = uuid4()

    runner = await service.get_runner(session_id)

    assert runner is not None
    assert hasattr(runner, "session_id")
    assert runner.session_id == session_id


@pytest.mark.asyncio
async def test_session_service_send_message(db_session: Any) -> None:
    """Test sending a message through the service."""
    from backend.app.services.session_service import SessionService

    service = SessionService(db_session)
    session_id = await service.create_session()

    response = await service.send_message(session_id, "Create a film about Ada Lovelace")

    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_session_service_reuses_runner() -> None:
    """Test that get_runner returns cached runner."""
    from backend.app.services.session_service import SessionService

    db_session = Mock()
    service = SessionService(db_session)
    session_id = uuid4()

    runner1 = await service.get_runner(session_id)
    runner2 = await service.get_runner(session_id)

    assert runner1 is runner2  # Same instance
