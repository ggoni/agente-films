"""Unit tests for ADKRunner."""

from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_adk_runner_initializes() -> None:
    """Test that ADKRunner can be initialized."""
    from backend.app.core.adk_runner import ADKRunner

    session_id = uuid4()
    session_manager = Mock()
    persistence_service = Mock()

    runner = ADKRunner(session_id, session_manager, persistence_service)

    assert runner.session_id == session_id
    assert runner.session_manager == session_manager
    assert runner.persistence_service == persistence_service


@pytest.mark.asyncio
async def test_adk_runner_initialize_creates_session() -> None:
    """Test that initialize method sets up ADK session."""
    from backend.app.core.adk_runner import ADKRunner

    session_id = uuid4()
    session_manager = Mock()
    session_manager.get_or_create_session.return_value = {"id": str(session_id)}
    persistence_service = Mock()

    runner = ADKRunner(session_id, session_manager, persistence_service)
    await runner.initialize()

    session_manager.get_or_create_session.assert_called_once_with(session_id)
    assert runner.adk_session is not None


@pytest.mark.asyncio
async def test_adk_runner_send_message_saves_question() -> None:
    """Test that send_message saves question to persistence."""
    from backend.app.core.adk_runner import ADKRunner

    session_id = uuid4()
    session_manager = Mock()
    session_manager.get_or_create_session.return_value = {"id": str(session_id)}
    
    persistence_service = Mock()
    persistence_service.save_question = Mock(return_value=uuid4())
    persistence_service.save_answer = Mock(return_value=uuid4())

    runner = ADKRunner(session_id, session_manager, persistence_service)
    await runner.initialize()

    message = "Create a film about Ada Lovelace"
    response = await runner.send_message(message)

    persistence_service.save_question.assert_called_once()
    call_args = persistence_service.save_question.call_args
    assert call_args[1]["session_id"] == session_id
    assert call_args[1]["question_text"] == message


@pytest.mark.asyncio
async def test_adk_runner_send_message_saves_answer() -> None:
    """Test that send_message saves answer to persistence."""
    from backend.app.core.adk_runner import ADKRunner

    session_id = uuid4()
    session_manager = Mock()
    session_manager.get_or_create_session.return_value = {"id": str(session_id)}
    
    persistence_service = Mock()
    persistence_service.save_question = Mock(return_value=uuid4())
    persistence_service.save_answer = Mock(return_value=uuid4())

    runner = ADKRunner(session_id, session_manager, persistence_service)
    await runner.initialize()

    await runner.send_message("Test message")

    persistence_service.save_answer.assert_called_once()
