"""Unit tests for PersistenceService."""

from typing import Any
from uuid import uuid4

import pytest


@pytest.mark.unit
def test_save_question(db_session: Any) -> None:  # noqa: F821
    """Test saving a question to database."""
    from backend.app.services.persistence_service import PersistenceService

    service = PersistenceService(db_session)
    session_id = uuid4()

    question_id = service.save_question(
        session_id=session_id,
        question_text="What is the plot about Ada Lovelace?",
        agent_name="greeter",
    )

    assert question_id is not None
    assert isinstance(question_id, type(uuid4()))


@pytest.mark.unit
def test_save_answer(db_session: Any) -> None:  # noqa: F821
    """Test saving an answer to database."""
    from backend.app.services.persistence_service import PersistenceService

    service = PersistenceService(db_session)
    session_id = uuid4()

    answer_id = service.save_answer(
        session_id=session_id,
        agent_name="researcher",
        answer_text="Ada Lovelace was a mathematician",
    )

    assert answer_id is not None
    assert isinstance(answer_id, type(uuid4()))


@pytest.mark.unit
def test_save_state_snapshot(db_session: Any) -> None:  # noqa: F821
    """Test saving state snapshot to database."""
    from backend.app.services.persistence_service import PersistenceService

    service = PersistenceService(db_session)
    session_id = uuid4()

    state = {
        "research": ["Ada was born in 1815"],
        "PLOT_OUTLINE": "A biographical drama about Ada Lovelace",
    }

    # Should not raise exception
    service.save_state_snapshot(session_id=session_id, state=state)


@pytest.mark.unit
def test_save_question_with_metadata(db_session: Any) -> None:  # noqa: F821
    """Test saving question with additional metadata."""
    from backend.app.services.persistence_service import PersistenceService

    service = PersistenceService(db_session)
    session_id = uuid4()

    metadata = {"source": "user_input", "priority": "high"}

    question_id = service.save_question(
        session_id=session_id,
        question_text="Create a film about Ada Lovelace",
        metadata=metadata,
    )

    assert question_id is not None
