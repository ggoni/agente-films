"""Unit tests for file_writer agent."""


def test_file_writer_agent_created() -> None:
    """Test that file_writer agent is created."""
    from backend.app.agents.file_writer import file_writer

    assert file_writer["name"] == "file_writer"


def test_file_writer_uses_correct_model() -> None:
    """Test that file_writer uses the correct model."""
    from backend.app.agents.file_writer import file_writer

    assert file_writer["model"] is not None
    assert isinstance(file_writer["model"], str)


def test_file_writer_has_description() -> None:
    """Test that file_writer has a description."""
    from backend.app.agents.file_writer import file_writer

    assert "description" in file_writer
    assert len(file_writer["description"]) > 0


def test_file_writer_has_instruction() -> None:
    """Test that file_writer has instruction text."""
    from backend.app.agents.file_writer import file_writer

    assert "instruction" in file_writer
    assert len(file_writer["instruction"]) > 0
    assert "pitch" in file_writer["instruction"].lower()


def test_file_writer_has_tools() -> None:
    """Test that file_writer has tools configured."""
    from backend.app.agents.file_writer import file_writer

    assert "tools" in file_writer
    assert len(file_writer["tools"]) > 0


def test_file_writer_has_write_file_tool() -> None:
    """Test that file_writer has write_file tool."""
    from backend.app.agents.file_writer import file_writer

    tool_names = [tool.__name__ for tool in file_writer["tools"]]
    assert "write_file" in tool_names
