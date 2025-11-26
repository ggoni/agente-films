"""Repository pattern for data access."""

from abc import ABC, abstractmethod
from typing import Any

from src.agents.screenplay_agent import ScreenplayAgent


class ScreenplayRepository(ABC):
    """Abstract repository for screenplay operations."""

    @abstractmethod
    async def generate_outline(self, concept: str, model: str) -> dict[str, Any]:
        """Generate screenplay outline.

        Args:
            concept: Movie concept
            model: LLM model to use

        Returns:
            Screenplay outline data
        """
        pass


class ADKScreenplayRepository(ScreenplayRepository):
    """Repository implementation using ADK agents."""

    def __init__(self) -> None:
        """Initialize repository."""
        self._agents: dict[str, ScreenplayAgent] = {}

    def _get_agent(self, model: str) -> ScreenplayAgent:
        """Get or create agent for model.

        Args:
            model: Model name

        Returns:
            ScreenplayAgent instance
        """
        if model not in self._agents:
            self._agents[model] = ScreenplayAgent(model=model)
        return self._agents[model]

    async def generate_outline(self, concept: str, model: str) -> dict[str, Any]:
        """Generate screenplay outline using ADK agent.

        Args:
            concept: Movie concept
            model: LLM model to use

        Returns:
            Screenplay outline data
        """
        agent = self._get_agent(model)
        result = await agent.create_outline(concept)

        # Add metadata
        result["agent_used"] = agent.agent.name

        return result
