"""Agent interaction API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["agents"])


class MessageRequest(BaseModel):
    """Request model for sending messages to agents."""

    message: str


class MessageResponse(BaseModel):
    """Response model for agent messages."""

    response: str
    session_id: str


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: UUID,
    request: MessageRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Send a message to the agent and get response.

    The message is processed by the greeter agent which coordinates
    the entire film concept generation workflow.

    Args:
        session_id: UUID of the session
        request: Message request containing user message
        db: Database session (injected)

    Returns:
        Agent response

    Raises:
        HTTPException: 404 if session not found, 500 for processing errors
    """
    try:
        service = SessionService(db)
        response_text = await service.send_message(session_id, request.message)

        return MessageResponse(
            response=response_text,
            session_id=str(session_id),
        )

    except Exception as e:
        # In production, log the error properly
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}",
        )
