"""Session management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.db.schemas import SessionResponse
from backend.app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(db: Session = Depends(get_db)) -> SessionResponse:
    """
    Create a new filmmaking session.

    Returns:
        Created session with ID and metadata
    """
    service = SessionService(db)
    session_id = await service.create_session()

    # Retrieve the created session to return full details
    from backend.app.db.repositories.session import SessionRepository

    repo = SessionRepository(db)
    session = repo.get_by_id(session_id)

    if not session:
        raise HTTPException(status_code=500, detail="Failed to create session")

    return SessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
) -> SessionResponse:
    """
    Get session by ID.

    Args:
        session_id: UUID of the session to retrieve

    Returns:
        Session details

    Raises:
        HTTPException: 404 if session not found
    """
    from backend.app.db.repositories.session import SessionRepository

    repo = SessionRepository(db)
    session = repo.get_by_id(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse.model_validate(session)
