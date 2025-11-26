"""Unit tests for box office analyst agent."""


def test_box_office_agent_created() -> None:
    """Test that box office analyst agent is created."""
    from backend.app.agents.box_office import box_office_analyst

    assert box_office_analyst.name == "box_office_researcher"


def test_box_office_has_output_key() -> None:
    """Test that box office analyst has output_key configured."""
    from backend.app.agents.box_office import box_office_analyst

    assert box_office_analyst.output_key == "box_office_report"


def test_box_office_has_description() -> None:
    """Test that box office analyst has a description."""
    from backend.app.agents.box_office import box_office_analyst

    assert box_office_analyst.description is not None
    assert len(box_office_analyst.description) > 0


def test_box_office_has_instruction() -> None:
    """Test that box office analyst has instructions."""
    from backend.app.agents.box_office import box_office_analyst

    assert box_office_analyst.instruction is not None
    assert len(box_office_analyst.instruction) > 0


def test_box_office_uses_correct_model() -> None:
    """Test that box office analyst uses the configured model."""
    from backend.app.agents.box_office import box_office_analyst

    assert box_office_analyst.model == "gemini-2.0-flash-exp"
