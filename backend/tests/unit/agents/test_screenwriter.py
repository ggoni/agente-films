"""Unit tests for screenwriter agent."""


def test_screenwriter_agent_created() -> None:
    """Test that screenwriter agent is created with correct name."""
    from backend.app.agents.screenwriter import screenwriter

    assert screenwriter.name == "screenwriter"


def test_screenwriter_has_output_key() -> None:
    """Test that screenwriter has output_key configured."""
    from backend.app.agents.screenwriter import screenwriter

    assert screenwriter.output_key == "PLOT_OUTLINE"


def test_screenwriter_has_description() -> None:
    """Test that screenwriter has a description."""
    from backend.app.agents.screenwriter import screenwriter

    assert screenwriter.description is not None
    assert len(screenwriter.description) > 0


def test_screenwriter_has_instruction() -> None:
    """Test that screenwriter has instructions."""
    from backend.app.agents.screenwriter import screenwriter

    assert screenwriter.instruction is not None
    assert len(screenwriter.instruction) > 0


def test_screenwriter_uses_correct_model() -> None:
    """Test that screenwriter uses the configured model."""
    from backend.app.agents.screenwriter import screenwriter

    assert screenwriter.model == "gemini-2.0-flash-exp"
