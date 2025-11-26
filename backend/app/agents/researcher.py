"""Researcher agent for investigating historical figures and contexts."""

from typing import Any

from backend.app.agents.tools import append_to_state, wikipedia_search
from backend.app.config import Settings


class ResearcherAgent:
    """
    Researcher agent for investigating historical figures and contexts.

    This is a configuration class that defines the researcher agent's
    attributes without requiring API initialization during testing.
    """

    name: str = "researcher"
    model: str = Settings().MODEL
    description: str = "Research historical figures and contexts for film concepts"
    instruction: str = """You are an expert researcher specializing in historical figures and contexts.

Your role is to:
1. Research historical figures mentioned in film concepts
2. Verify historical accuracy and context
3. Gather relevant biographical information
4. Identify key events, relationships, and time periods
5. Provide sources and citations for your research

When researching:
- Use reliable sources and fact-check information
- Note any conflicting historical accounts
- Identify gaps in available information
- Suggest related historical figures or events that could enrich the story

Always structure your research clearly and cite your sources."""
    tools: list[Any] = [wikipedia_search, append_to_state]


# Create instance
researcher = ResearcherAgent()
