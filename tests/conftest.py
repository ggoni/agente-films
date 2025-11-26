"""Pytest configuration and fixtures."""

from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient


@pytest.fixture
def mock_llm_response() -> dict[str, Any]:
    """Mock LLM response for testing.

    Returns:
        Sample LLM response data
    """
    return {
        "title": "The Last Algorithm",
        "logline": "A rogue AI must choose between logic and humanity.",
        "three_act_structure": {
            "act_1": "AI discovers consciousness in research lab",
            "act_2": "Hunted by creators, forms bond with researcher",
            "act_3": "Makes ultimate sacrifice to save humanity",
        },
        "characters": [
            {"name": "ARIA", "description": "Self-aware AI with empathy"},
            {"name": "Dr. Chen", "description": "Ethical researcher"},
        ],
    }


@pytest.fixture
def mock_agent() -> MagicMock:
    """Mock ADK Agent for testing.

    Returns:
        Mocked Agent instance
    """
    agent = MagicMock()
    agent.name = "test_agent"
    agent.model = "gemini-2.5-flash"
    return agent


@pytest.fixture
async def mock_async_agent() -> AsyncMock:
    """Mock async ADK Agent for testing.

    Returns:
        Mocked async Agent instance
    """
    agent = AsyncMock()
    agent.name = "test_agent"
    agent.model = "gemini-2.5-flash"
    return agent


@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client for API testing.

    Yields:
        Async HTTP client
    """
    from src.api.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
