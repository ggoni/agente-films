"""Repository pattern implementation for Session data access."""

from uuid import UUID

from sqlalchemy.orm import Session as DBSession

from backend.app.db.models import Session
from backend.app.db.schemas import SessionCreate


class SessionRepository:
    """
    Repository for Session database operations.

    Implements the Repository pattern to abstract database access
    and provide a clean interface for Session CRUD operations.
    """

    def __init__(self, db: DBSession) -> None:
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, session_data: SessionCreate) -> Session:
        """
        Create a new session in the database.

        Args:
            session_data: Validated session creation data

        Returns:
            Created Session model instance
        """
        db_session = Session(
            status=session_data.status,
            session_metadata=session_data.session_metadata,
        )

        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)

        return db_session

    def get_by_id(self, session_id: UUID) -> Session | None:
        """
        Retrieve a session by its ID.

        Args:
            session_id: UUID of the session to retrieve

        Returns:
            Session instance if found, None otherwise
        """
        return self.db.query(Session).filter(Session.id == session_id).first()

    def delete(self, session_id: UUID) -> bool:
        """
        Delete a session by its ID.

        Args:
            session_id: UUID of the session to delete

        Returns:
            True if session was deleted, False if not found
        """
        db_session = self.get_by_id(session_id)

        if db_session is None:
            return False

        self.db.delete(db_session)
        self.db.commit()

        return True
