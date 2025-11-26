"""Pytest fixtures and configuration."""

from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.db.base import Base

# Import all models to register them with Base.metadata
from backend.app.db.models import Answer, Question, Session as SessionModel, SessionState  # noqa: F401


@pytest.fixture(scope="function")
def db_engine() -> Generator[Engine, None, None]:
    """Create an in-memory SQLite database engine for testing."""
    # Add check_same_thread=False for FastAPI async compatibility
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine: Engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> Generator:
    """
    Create FastAPI test client with database dependency overridden.
    
    This fixture ensures all API endpoint tests use the same test database session.
    """
    from fastapi.testclient import TestClient
    
    from backend.app.api.dependencies import get_db
    from backend.app.api.main import app
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # db_session cleanup handled by its own fixture
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
