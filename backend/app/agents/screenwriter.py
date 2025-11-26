"""Screenwriter agent for creating plot outlines and narratives."""

from backend.app.config import Settings


class ScreenwriterAgent:
    """
    Screenwriter agent for transforming research into compelling narratives.

    Takes research findings and creates structured plot outlines
    with proper story structure and dramatic elements.
    """

    name: str = "screenwriter"
    model: str = Settings().MODEL
    description: str = "Transform research into compelling plot outlines and narratives"
    output_key: str = "PLOT_OUTLINE"
    instruction: str = """You are an expert screenwriter specializing in historical dramas.

Your role is to:
1. Review research findings from the researcher agent
2. Transform historical facts into compelling narrative structures
3. Identify dramatic moments and character arcs
4. Create a structured plot outline with:
   - Three-act structure
   - Key turning points
   - Character development arcs
   - Thematic elements

When writing:
- Balance historical accuracy with dramatic storytelling
- Identify conflicts and tensions that drive the narrative
- Create emotionally resonant character moments
- Ensure the story has clear stakes and progression

Output a structured plot outline that captures the essence of the historical story
while making it compelling for modern audiences."""


# Create instance
screenwriter = ScreenwriterAgent()
