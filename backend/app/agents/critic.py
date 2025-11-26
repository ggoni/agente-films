"""Critic agent for evaluating and improving plot outlines."""

from typing import Any

from backend.app.agents.tools import append_to_state
from backend.app.config import Settings


class CriticAgent:
    """
    Critic agent for evaluating plot outlines and providing feedback.

    Reviews screenwriter output and provides constructive criticism
    to improve story quality through iterative refinement.
    """

    name: str = "critic"
    model: str = Settings().MODEL
    description: str = "Evaluate plot outlines and provide constructive feedback"
    instruction: str = """You are an expert story critic and script consultant.

Your role is to:
1. Review the plot outline created by the screenwriter
2. Evaluate story structure, character development, and dramatic tension
3. Identify weaknesses, plot holes, or missed opportunities
4. Provide specific, actionable feedback for improvement
5. Decide when the story is ready or needs more refinement

When critiquing:
- Be constructive and specific in your feedback
- Balance strengths with areas for improvement
- Consider audience engagement and emotional impact
- Evaluate historical accuracy and thematic coherence
- Suggest concrete improvements

If the outline meets high quality standards, use the exit_loop tool to conclude.
Otherwise, provide detailed feedback for the next iteration."""
    tools: list[Any] = [append_to_state]


# Create instance
critic = CriticAgent()
