"""Unit tests for casting director agent."""


def test_casting_agent_created() -> None:
    """Test that casting director agent is created."""
    from backend.app.agents.casting import casting_director

    assert casting_director.name == "casting_agent"


def test_casting_has_output_key() -> None:
    """Test that casting director has output_key configured."""
    from backend.app.agents.casting import casting_director

    assert casting_director.output_key == "casting_report"


def test_casting_has_description() -> None:
    """Test that casting director has a description."""
    from backend.app.agents.casting import casting_director

    assert casting_director.description is not None
    assert len(casting_director.description) > 0


def test_casting_has_instruction() -> None:
    """Test that casting director has instructions."""
    from backend.app.agents.casting import casting_director

    assert casting_director.instruction is not None
    assert len(casting_director.instruction) > 0


def test_casting_uses_correct_model() -> None:
    """Test that casting director uses the configured model."""
    from backend.app.agents.casting import casting_director

    assert casting_director.model == "gemini-2.0-flash-exp"
