"""API models and schemas."""

from pydantic import BaseModel, Field


class ScreenplayRequest(BaseModel):
    """Request model for screenplay generation."""

    concept: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Movie concept or premise",
        examples=["A detective who can see the future must prevent a crime"],
    )
    model: str | None = Field(
        default="gemini-2.5-flash",
        description="LLM model to use for generation",
    )


class CharacterSchema(BaseModel):
    """Character information."""

    name: str
    description: str


class ThreeActStructure(BaseModel):
    """Three-act screenplay structure."""

    act_1: str = Field(..., description="Setup and introduction")
    act_2: str = Field(..., description="Confrontation and development")
    act_3: str = Field(..., description="Resolution and climax")


class ScreenplayResponse(BaseModel):
    """Response model for screenplay outline."""

    title: str = Field(..., description="Movie title")
    logline: str = Field(..., description="One-line story summary")
    three_act_structure: ThreeActStructure
    characters: list[CharacterSchema]
    agent_used: str = Field(..., description="Agent that generated content")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str
    error_code: str | None = None
