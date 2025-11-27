"""Unit tests for greeter agent (root agent)."""


def test_greeter_agent_created() -> None:
    """Test that greeter agent is created."""
    from backend.app.agents.greeter import greeter

    assert greeter["name"] == "greeter"


def test_greeter_uses_correct_model() -> None:
    """Test that greeter uses the correct model."""
    from backend.app.agents.greeter import greeter

    assert greeter["model"] is not None
    assert isinstance(greeter["model"], str)


def test_greeter_has_description() -> None:
    """Test that greeter has a description."""
    from backend.app.agents.greeter import greeter

    assert "description" in greeter
    assert len(greeter["description"]) > 0


def test_greeter_has_instruction() -> None:
    """Test that greeter has instruction text."""
    from backend.app.agents.greeter import greeter

    assert "instruction" in greeter
    assert len(greeter["instruction"]) > 0
    assert "welcome" in greeter["instruction"].lower()


def test_greeter_has_sub_agents() -> None:
    """Test that greeter has sub-agents configured."""
    from backend.app.agents.greeter import greeter

    assert "sub_agents" in greeter
    assert len(greeter["sub_agents"]) > 0


def test_greeter_has_film_concept_team() -> None:
    """Test that greeter has film_concept_team as sub-agent."""
    from backend.app.agents.greeter import greeter

    # Get name from sub-agent (could be dict or object)
    sub_agent = greeter["sub_agents"][0]
    agent_name = sub_agent["name"] if isinstance(sub_agent, dict) else sub_agent.name

    assert agent_name == "film_concept_team"
