"""Database base configuration and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.app.config import Settings

# Declarative base for all models
Base = declarative_base()

# Singleton engine instance
_engine: Engine | None = None


def get_engine() -> Engine:
    """
    Get or create SQLAlchemy engine with connection pooling.

    Returns:
        Engine: Configured SQLAlchemy engine instance (singleton)
    """
    global _engine

    if _engine is None:
        settings = Settings()
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )

    return _engine


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that provides database session.

    Yields:
        Session: SQLAlchemy session for database operations

    Example:
        ```python
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            return session.query(Item).all()
        ```
    """
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
