"""ADK Runner for executing agent workflows with persistence."""

from typing import Any
from uuid import UUID

from backend.app.core.session_manager import SessionManager
from backend.app.services.persistence_service import PersistenceService


class ADKRunner:
    """
    Wraps Google ADK Runner with session management and persistence.

    Coordinates ADK agent execution with SessionManager for session caching
    and PersistenceService for tracking all questions, answers, and state.
    """

    def __init__(
        self,
        session_id: UUID,
        session_manager: SessionManager,
        persistence_service: PersistenceService,
    ) -> None:
        """
        Initialize ADK Runner.

        Args:
            session_id: Unique session identifier
            session_manager: Session manager for ADK session caching
            persistence_service: Service for persisting Q&A and state
        """
        self.session_id = session_id
        self.session_manager = session_manager
        self.persistence_service = persistence_service
        self.adk_session: Any = None
        self.runner: Any = None

    async def initialize(self) -> None:
        """
        Initialize ADK runner with session.

        Creates or retrieves cached ADK session and sets up the runner
        with the greeter root agent.

        Note:
            In production with actual Google ADK:
            from google.adk import Runner
            from backend.app.agents.greeter import greeter
            self.runner = Runner(agent=greeter, session=self.adk_session)
        """
        # Get or create ADK session from cache
        self.adk_session = self.session_manager.get_or_create_session(self.session_id)

        # Placeholder: In production, create actual ADK Runner
        # For now, create a simple mock runner
        self.runner = {
            "session": self.adk_session,
            "agent": "greeter",
            "initialized": True,
        }

    async def send_message(self, message: str) -> str:
        """
        Send message to agent and get response.

        Saves question to persistence, executes agent workflow,
        and saves answer to persistence.

        Args:
            message: User message to send to agent

        Returns:
            Agent response text

        Note:
            In production with actual Google ADK:
            response = await self.runner.run(message)
            return response.text
        """
        if not self.runner:
            await self.initialize()

        # Save question to database
        self.persistence_service.save_question(
            session_id=self.session_id,
            question_text=message,
            agent_name="user",
        )

        # Placeholder: Execute agent workflow
        # In production, this would call the actual ADK runner
        response_text = f"Processed: {message}"

        # Save answer to database
        self.persistence_service.save_answer(
            session_id=self.session_id,
            agent_name="greeter",
            answer_text=response_text,
        )

        return response_text

    async def save_state_snapshot(self, state: dict[str, Any]) -> None:
        """
        Save current session state snapshot.

        Args:
            state: State dictionary to snapshot
        """
        self.persistence_service.save_state_snapshot(
            session_id=self.session_id,
            state=state,
        )
