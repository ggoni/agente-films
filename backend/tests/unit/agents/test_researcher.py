"""Unit tests for researcher agent."""

import pytest
from google.genai.types import Tool


def test_researcher_agent_created() -> None:
    """Test that researcher agent is created with correct name."""
    from backend.app.agents.researcher import researcher

    assert researcher.name == "researcher"


def test_researcher_has_description() -> None:
    """Test that researcher agent has a description."""
    from backend.app.agents.researcher import researcher

    assert researcher.description is not None
    assert len(researcher.description) > 0
    assert "research" in researcher.description.lower()


def test_researcher_has_instruction() -> None:
    """Test that researcher agent has instructions."""
    from backend.app.agents.researcher import researcher

    assert researcher.instruction is not None
    assert len(researcher.instruction) > 0


def test_researcher_uses_correct_model() -> None:
    """Test that researcher agent uses the configured model."""
    from backend.app.agents.researcher import researcher

    assert researcher.model == "gemini-2.0-flash-exp"


def test_researcher_has_tools() -> None:
    """Test that researcher agent has tools configured."""
    from backend.app.agents.researcher import researcher

    # Initially may not have tools, but should have the tools attribute
    assert hasattr(researcher, "tools")
    # Tools list should be a list (empty or populated)
    assert isinstance(researcher.tools, list)
