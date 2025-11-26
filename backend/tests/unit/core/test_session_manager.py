"""Unit tests for SessionManager."""

from uuid import uuid4


def test_session_manager_creates_new_session() -> None:
    """Test that SessionManager creates a new session."""
    from backend.app.core.session_manager import SessionManager

    manager = SessionManager()
    session_id = uuid4()
    session = manager.get_or_create_session(session_id)

    assert session is not None


def test_session_manager_returns_cached_session() -> None:
    """Test that SessionManager returns the same cached session."""
    from backend.app.core.session_manager import SessionManager

    manager = SessionManager()
    session_id = uuid4()
    
    session1 = manager.get_or_create_session(session_id)
    session2 = manager.get_or_create_session(session_id)

    assert session1 is session2  # Same object in memory


def test_session_manager_creates_different_sessions() -> None:
    """Test that different session IDs get different sessions."""
    from backend.app.core.session_manager import SessionManager

    manager = SessionManager()
    session_id1 = uuid4()
    session_id2 = uuid4()

    session1 = manager.get_or_create_session(session_id1)
    session2 = manager.get_or_create_session(session_id2)

    assert session1 is not session2


def test_session_manager_multiple_ids() -> None:
    """Test that SessionManager handles multiple session IDs correctly."""
    from backend.app.core.session_manager import SessionManager

    manager = SessionManager()
    sessions = {}
    
    # Create 5 different sessions
    for i in range(5):
        session_id = uuid4()
        sessions[session_id] = manager.get_or_create_session(session_id)
    
    # Verify they're all cached correctly
    for session_id, original_session in sessions.items():
        cached_session = manager.get_or_create_session(session_id)
        assert cached_session is original_session
