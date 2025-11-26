"""FastAPI dependency injection functions."""

from typing import Generator

from sqlalchemy.orm import Session

from backend.app.db.base import get_session


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    Yields:
        SQLAlchemy database session

    Example:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    yield from get_session()
