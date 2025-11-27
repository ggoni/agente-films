"""Persistence service for tracking questions, answers, and state."""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.db.models import Answer, Question, SessionState
from backend.app.db.schemas import AnswerCreate, QuestionCreate, SessionStateCreate


class PersistenceService:
    """
    Service for persisting agent questions, answers, and state snapshots.

    Handles database operations for tracking all agent interactions
    and state changes throughout a filmmaking session.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize persistence service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def save_question(
        self,
        session_id: UUID,
        question_text: str,
        agent_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        """
        Save a question to the database.

        Args:
            session_id: Session identifier
            question_text: The question text
            agent_name: Optional agent name
            metadata: Optional additional metadata

        Returns:
            UUID of the created question
        """
        question_data = QuestionCreate(
            session_id=session_id,
            question_text=question_text,
            agent_name=agent_name,
            question_metadata=metadata,
        )

        question = Question(
            session_id=question_data.session_id,
            question_text=question_data.question_text,
            agent_name=question_data.agent_name,
            question_metadata=question_data.question_metadata,
        )

        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)

        return question.id

    def save_answer(
        self,
        session_id: UUID,
        agent_name: str,
        answer_text: str,
        question_id: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        """
        Save an answer to the database.

        Args:
            session_id: Session identifier
            agent_name: Name of the agent providing the answer
            answer_text: The answer text
            question_id: Optional question this answers
            metadata: Optional additional metadata

        Returns:
            UUID of the created answer
        """
        answer_data = AnswerCreate(
            session_id=session_id,
            question_id=question_id,
            agent_name=agent_name,
            answer_text=answer_text,
            answer_metadata=metadata,
        )

        answer = Answer(
            session_id=answer_data.session_id,
            question_id=answer_data.question_id,
            agent_name=answer_data.agent_name,
            answer_text=answer_data.answer_text,
            answer_metadata=answer_data.answer_metadata,
        )

        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)

        return answer.id

    def save_state_snapshot(
        self,
        session_id: UUID,
        state: dict[str, Any],
        state_key: str = "full_state",
        version: int = 1,
    ) -> None:
        """
        Save a snapshot of session state.

        Args:
            session_id: Session identifier
            state: State dictionary to save
            state_key: Key identifier for this state
            version: Version number for this state
        """
        state_data = SessionStateCreate(
            session_id=session_id,
            state_key=state_key,
            state_value=state,
            version=version,
        )

        session_state = SessionState(
            session_id=state_data.session_id,
            state_key=state_data.state_key,
            state_value=state_data.state_value,
            version=state_data.version,
        )

        self.db.add(session_state)
        self.db.commit()
