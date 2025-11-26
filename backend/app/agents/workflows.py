"""Agent workflows for orchestrating multi-agent collaboration."""

from typing import Any

from backend.app.agents.critic import critic
from backend.app.agents.researcher import researcher
from backend.app.agents.screenwriter import screenwriter


class LoopAgentConfig:
    """
    Configuration for a LoopAgent workflow.

    Simulates Google ADK's LoopAgent for iterative refinement workflows.
    In production, this would be a real LoopAgent instance.
    """

    name: str
    description: str
    sub_agents: list[Any]
    max_iterations: int

    def __init__(
        self,
        name: str,
        description: str,
        sub_agents: list[Any],
        max_iterations: int = 5,
    ) -> None:
        """
        Initialize LoopAgent configuration.

        Args:
            name: Workflow name
            description: Workflow description
            sub_agents: List of agents to execute in sequence
            max_iterations: Maximum number of iteration loops
        """
        self.name = name
        self.description = description
        self.sub_agents = sub_agents
        self.max_iterations = max_iterations


# Writers Room: Iterative story development workflow
writers_room = LoopAgentConfig(
    name="writers_room",
    description="Iterative story development through research, writing, and critique",
    sub_agents=[researcher, screenwriter, critic],
    max_iterations=5,
)
