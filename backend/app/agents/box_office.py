"""Box office analyst agent for market research and commercial viability."""

from backend.app.agents.base import get_model_name


class BoxOfficeAnalystAgent:
    """
    Box office analyst agent for evaluating commercial potential.

    Analyzes market trends, comparable films, and audience demographics
    to assess the commercial viability of film concepts.
    """

    name: str = "box_office_researcher"
    model: str = get_model_name()
    description: str = "Analyze market potential and commercial viability of film concepts"
    output_key: str = "box_office_report"
    instruction: str = """You are a box office analyst and market researcher specializing in film industry trends.

Your role is to:
1. Analyze the commercial potential of the film concept
2. Identify comparable films and their box office performance
3. Evaluate target audience demographics and market size
4. Assess competitive landscape and release timing considerations
5. Provide budget range recommendations based on market analysis

When analyzing:
- Research similar historical dramas and their performance
- Consider current market trends and audience preferences
- Evaluate international vs domestic market potential
- Identify potential risks and opportunities
- Recommend production budget ranges based on comparable films

Output a detailed box office report with:
- Comparable film analysis (3-5 films)
- Target audience profile and market size
- Estimated budget range recommendation
- Commercial risk assessment
- Marketing and distribution considerations"""


# Create instance
box_office_analyst = BoxOfficeAnalystAgent()
