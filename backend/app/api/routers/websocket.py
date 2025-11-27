"""WebSocket endpoint for streaming agent responses."""

from contextlib import suppress
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_db
from backend.app.services.session_service import SessionService

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    WebSocket endpoint for real-time agent communication.

    Allows streaming responses from agents as they're generated,
    providing a better UX for long-running agent workflows.

    Args:
        websocket: WebSocket connection
        session_id: UUID of the session
        db: Database session (injected)

    Example client usage:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/ws/sessions/{id}');
        ws.onmessage = (event) => console.log(event.data);
        ws.send(JSON.stringify({message: "Create a film about Ada Lovelace"}));
        ```
    """
    await websocket.accept()

    try:
        service = SessionService(db)

        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")

            if not message:
                await websocket.send_json({
                    "type": "error",
                    "content": "Message cannot be empty",
                })
                continue

            # Send acknowledgment
            await websocket.send_json({
                "type": "status",
                "content": "Processing your message...",
            })

            try:
                # Process message through agent
                response = await service.send_message(session_id, message)

                # Send complete response
                await websocket.send_json({
                    "type": "response",
                    "content": response,
                    "session_id": str(session_id),
                })

            except Exception as e:
                # Send error to client
                await websocket.send_json({
                    "type": "error",
                    "content": f"Error processing message: {str(e)}",
                })

    except WebSocketDisconnect:
        # Client disconnected
        pass
    except Exception as e:
        # Unexpected error
        with suppress(Exception):
            await websocket.send_json({
                "type": "error",
                "content": f"Server error: {str(e)}",
            })
