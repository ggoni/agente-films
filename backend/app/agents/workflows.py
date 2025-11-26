"""Agent workflows for orchestrating multi-agent collaboration."""

from typing import Any

from backend.app.agents.box_office import box_office_analyst
from backend.app.agents.casting import casting_director
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


class ParallelAgentConfig:
    """
    Configuration for a ParallelAgent workflow.

    Simulates Google ADK's ParallelAgent for concurrent execution.
    In production, this would be a real ParallelAgent instance.
    """

    name: str
    description: str
    sub_agents: list[Any]

    def __init__(
        self,
        name: str,
        description: str,
        sub_agents: list[Any],
    ) -> None:
        """
        Initialize ParallelAgent configuration.

        Args:
            name: Workflow name
            description: Workflow description
            sub_agents: List of agents to execute in parallel
        """
        self.name = name
        self.description = description
        self.sub_agents = sub_agents


class SequentialAgentConfig:
    """
    Configuration for a SequentialAgent workflow.

    Simulates Google ADK's SequentialAgent for step-by-step execution.
    In production, this would be a real SequentialAgent instance.
    """

    name: str
    description: str
    sub_agents: list[Any]

    def __init__(
        self,
        name: str,
        description: str,
        sub_agents: list[Any],
    ) -> None:
        """
        Initialize SequentialAgent configuration.

        Args:
            name: Workflow name
            description: Workflow description
            sub_agents: List of agents/workflows to execute sequentially
        """
        self.name = name
        self.description = description
        self.sub_agents = sub_agents


# Writers Room: Iterative story development workflow
writers_room = LoopAgentConfig(
    name="writers_room",
    description="Iterative story development through research, writing, and critique",
    sub_agents=[researcher, screenwriter, critic],
    max_iterations=5,
)

# Preproduction Team: Parallel market and casting analysis
preproduction_team = ParallelAgentConfig(
    name="preproduction_team",
    description="Parallel analysis of market potential and casting options",
    sub_agents=[box_office_analyst, casting_director],
)

# Import file_writer after workflows to avoid circular dependency
from backend.app.agents.file_writer import file_writer  # noqa: E402

# Film Concept Team: Complete sequential workflow
film_concept_team = SequentialAgentConfig(
    name="film_concept_team",
    description="Complete film pitch development workflow from concept to final document",
    sub_agents=[writers_room, preproduction_team, file_writer],
)

