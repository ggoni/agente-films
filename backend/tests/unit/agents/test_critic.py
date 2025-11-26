"""Unit tests for critic agent."""


def test_critic_agent_created() -> None:
    """Test that critic agent is created with correct name."""
    from backend.app.agents.critic import critic

    assert critic.name == "critic"


def test_critic_has_tools() -> None:
    """Test that critic has tools configured."""
    from backend.app.agents.critic import critic

    assert hasattr(critic, "tools")
    assert isinstance(critic.tools, list)
    assert len(critic.tools) > 0


def test_critic_has_append_to_state_tool() -> None:
    """Test that critic has append_to_state tool."""
    from backend.app.agents.critic import critic

    tool_names = [t.__name__ for t in critic.tools]
    assert "append_to_state" in tool_names


def test_critic_has_description() -> None:
    """Test that critic has a description."""
    from backend.app.agents.critic import critic

    assert critic.description is not None
    assert len(critic.description) > 0


def test_critic_has_instruction() -> None:
    """Test that critic has instructions."""
    from backend.app.agents.critic import critic

    assert critic.instruction is not None
    assert len(critic.instruction) > 0


def test_critic_uses_correct_model() -> None:
    """Test that critic uses the configured model."""
    from backend.app.agents.critic import critic

    assert critic.model == "gemini-2.0-flash-exp"
