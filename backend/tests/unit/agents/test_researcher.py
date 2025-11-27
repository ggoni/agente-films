"""Unit tests for researcher agent."""



def test_researcher_agent_created() -> None:
    """Test that researcher agent is created with correct name."""
    from backend.app.agents.researcher import researcher

    assert researcher.name == "researcher"


def test_researcher_has_description() -> None:
    """Test that researcher agent has a description."""
    from backend.app.agents.researcher import researcher

    assert researcher.description is not None
    assert len(researcher.description) > 0
    assert "research" in researcher.description.lower()


def test_researcher_has_instruction() -> None:
    """Test that researcher agent has instructions."""
    from backend.app.agents.researcher import researcher

    assert researcher.instruction is not None
    assert len(researcher.instruction) > 0


def test_researcher_uses_correct_model() -> None:
    """Test that researcher agent uses the configured model."""
    from backend.app.agents.researcher import researcher

    assert researcher.model == "gemini-2.0-flash-exp"


def test_researcher_has_tools() -> None:
    """Test that researcher agent has tools configured."""
    from backend.app.agents.researcher import researcher

    # Should have tools attribute and it should be populated
    assert hasattr(researcher, "tools")
    assert isinstance(researcher.tools, list)
    assert len(researcher.tools) > 0


def test_researcher_has_wikipedia_tool() -> None:
    """Test that researcher has wikipedia_search tool."""
    from backend.app.agents.researcher import researcher

    tool_names = [t.__name__ for t in researcher.tools]
    assert "wikipedia_search" in tool_names


def test_researcher_has_append_to_state_tool() -> None:
    """Test that researcher has append_to_state tool."""
    from backend.app.agents.researcher import researcher

    tool_names = [t.__name__ for t in researcher.tools]
    assert "append_to_state" in tool_names
