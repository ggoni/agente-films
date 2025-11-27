"""Integration test fixtures."""

from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.dependencies import get_db
from backend.app.api.main import app
from backend.app.config import Settings

# Use the local database URL from environment or default to the one we set up
# Note: In a real CI env, we might use a separate test DB
settings = Settings()
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Yield the database engine."""
    yield engine


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Yield a database session for testing.
    Wraps the test in a transaction and rolls it back after.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
async def async_client(db_session: Session) -> AsyncGenerator[AsyncClient, None]:
    """
    Yield an async test client with overridden DB dependency.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Use ASGITransport for direct app testing without a server
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
