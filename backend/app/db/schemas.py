"""Pydantic schemas for data validation and serialization."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SessionBase(BaseModel):
    """Base schema for Session with common fields."""

    status: str = Field(
        default="active",
        description="Session status: active, completed, failed, cancelled",
    )
    session_metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional session metadata as JSON",
    )


class SessionCreate(SessionBase):
    """Schema for creating a new Session."""

    pass


class SessionResponse(SessionBase):
    """Schema for Session responses from API."""

    id: UUID = Field(description="Unique session identifier")
    created_at: datetime = Field(description="Session creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "active",
                "session_metadata": {"user_id": "user_123", "source": "web"},
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        },
    )
