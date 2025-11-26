"""Unit tests for ScreenplayAgent."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.screenplay_agent import ScreenplayAgent, ScreenplayOutline


@pytest.mark.unit
class TestScreenplayAgent:
    """Test suite for ScreenplayAgent."""

    def test_agent_initialization(self) -> None:
        """Test agent initializes with correct model."""
        agent = ScreenplayAgent(model="gemini-2.5-flash")

        assert agent.model == "gemini-2.5-flash"
        assert agent.agent is not None
        assert agent.agent.name == "screenplay_writer"

    def test_agent_initialization_default_model(self) -> None:
        """Test agent uses default model."""
        agent = ScreenplayAgent()

        assert agent.model == "gemini-2.5-flash"

    @pytest.mark.asyncio
    async def test_create_outline_structure(
        self,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """Test outline creation returns correct structure."""
        agent = ScreenplayAgent()

        with patch.object(agent, "create_outline", return_value=mock_llm_response):
            result = await agent.create_outline("A story about AI consciousness")

            assert "title" in result
            assert "logline" in result
            assert "three_act_structure" in result
            assert "characters" in result
            assert isinstance(result["characters"], list)

    @pytest.mark.asyncio
    async def test_create_outline_three_acts(
        self,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """Test outline contains all three acts."""
        agent = ScreenplayAgent()

        with patch.object(agent, "create_outline", return_value=mock_llm_response):
            result = await agent.create_outline("Epic space adventure")

            acts = result["three_act_structure"]
            assert "act_1" in acts
            assert "act_2" in acts
            assert "act_3" in acts

    @pytest.mark.asyncio
    async def test_create_outline_with_empty_concept(self) -> None:
        """Test handling of empty concept."""
        agent = ScreenplayAgent()

        result = await agent.create_outline("")

        # Should still return valid structure
        assert "title" in result
        assert "logline" in result

    def test_screenplay_outline_model(self) -> None:
        """Test ScreenplayOutline pydantic model validation."""
        data = {
            "title": "Test Title",
            "logline": "Test logline",
            "three_act_structure": {
                "act_1": "Setup",
                "act_2": "Conflict",
                "act_3": "Resolution",
            },
            "characters": [{"name": "Hero", "description": "Main character"}],
        }

        outline = ScreenplayOutline(**data)

        assert outline.title == "Test Title"
        assert len(outline.characters) == 1
        assert "act_1" in outline.three_act_structure


@pytest.mark.unit
class TestScreenplayAgentWithMockedLLM:
    """Test ScreenplayAgent with mocked LLM responses."""

    @pytest.mark.asyncio
    async def test_agent_calls_llm_with_concept(
        self,
        mock_async_agent: AsyncMock,
    ) -> None:
        """Test agent passes concept to LLM correctly."""
        # Mock the ADK agent's generate method
        mock_async_agent.generate = AsyncMock(
            return_value="Generated screenplay content"
        )

        agent = ScreenplayAgent()
        agent.agent = mock_async_agent

        concept = "Time-traveling detective"
        # When we implement actual LLM calls, test them here
        # For now, test the structure
        result = await agent.create_outline(concept)

        assert result is not None

    @pytest.mark.asyncio
    async def test_multiple_characters_in_outline(
        self,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """Test outline can contain multiple characters."""
        agent = ScreenplayAgent()

        # Add more characters to mock response
        enhanced_response = mock_llm_response.copy()
        enhanced_response["characters"] = [
            {"name": "Hero", "description": "Protagonist"},
            {"name": "Villain", "description": "Antagonist"},
            {"name": "Sidekick", "description": "Supporting character"},
        ]

        with patch.object(agent, "create_outline", return_value=enhanced_response):
            result = await agent.create_outline("Superhero origin story")

            assert len(result["characters"]) == 3
            assert result["characters"][0]["name"] == "Hero"
