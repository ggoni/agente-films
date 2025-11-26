"""SQLAlchemy ORM models for database tables."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Session(Base):
    """
    Session model representing a user interaction session.

    Tracks the lifecycle of a filmmaking concept generation session,
    including all questions, answers, and agent interactions.
    """

    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        comment="Session status: active, completed, failed, cancelled",
    )

    session_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Additional session metadata stored as JSON",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        """String representation of Session."""
        return f"<Session(id={self.id}, status={self.status})>"
