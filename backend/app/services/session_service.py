"""Session service for high-level business logic orchestration."""

from uuid import UUID

from sqlalchemy.orm import Session

from backend.app.core.adk_runner import ADKRunner
from backend.app.core.session_manager import SessionManager
from backend.app.db.repositories.session import SessionRepository
from backend.app.db.schemas import SessionCreate
from backend.app.services.persistence_service import PersistenceService


class SessionService:
    """
    High-level session business logic service.

    Orchestrates SessionRepository, SessionManager, ADKRunner, and
    PersistenceService to provide a clean API for session management
    and agent interaction.
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize session service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.session_repository = SessionRepository(db)
        self.session_manager = SessionManager()
        self.persistence_service = PersistenceService(db)
        self._runners: dict[UUID, ADKRunner] = {}

    async def create_session(self) -> UUID:
        """
        Create a new session in the database.

        Returns:
            UUID of the created session
        """
        session_data = SessionCreate(status="active")
        session = self.session_repository.create(session_data)
        return session.id

    async def get_runner(self, session_id: UUID) -> ADKRunner:
        """
        Get or create ADK runner for a session.

        Caches runners in memory to avoid re-initialization.

        Args:
            session_id: Session identifier

        Returns:
            ADKRunner instance for the session
        """
        if session_id not in self._runners:
            runner = ADKRunner(
                session_id=session_id,
                session_manager=self.session_manager,
                persistence_service=self.persistence_service,
            )
            await runner.initialize()
            self._runners[session_id] = runner

        return self._runners[session_id]

    async def send_message(self, session_id: UUID, message: str) -> str:
        """
        Send a message to the agent and get response.

        Handles the complete flow:
        1. Get or create ADK runner
        2. Send message (which persists Q&A automatically)
        3. Return response

        Args:
            session_id: Session identifier
            message: User message

        Returns:
            Agent response text
        """
        runner = await self.get_runner(session_id)
        response = await runner.send_message(message)
        return response
