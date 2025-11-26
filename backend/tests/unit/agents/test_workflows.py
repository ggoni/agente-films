"""Unit tests for agent workflows."""


def test_writers_room_exists() -> None:
    """Test that writers_room workflow is defined."""
    from backend.app.agents.workflows import writers_room

    assert writers_room is not None


def test_writers_room_has_name() -> None:
    """Test that writers_room has correct name."""
    from backend.app.agents.workflows import writers_room

    assert writers_room.name == "writers_room"


def test_writers_room_has_description() -> None:
    """Test that writers_room has a description."""
    from backend.app.agents.workflows import writers_room

    assert writers_room.description is not None
    assert len(writers_room.description) > 0


def test_writers_room_has_sub_agents() -> None:
    """Test that writers_room has sub-agents configured."""
    from backend.app.agents.workflows import writers_room

    assert hasattr(writers_room, "sub_agents")
    assert isinstance(writers_room.sub_agents, list)
    assert len(writers_room.sub_agents) == 3


def test_writers_room_max_iterations() -> None:
    """Test that writers_room has max_iterations set."""
    from backend.app.agents.workflows import writers_room

    assert hasattr(writers_room, "max_iterations")
    assert writers_room.max_iterations == 5


def test_writers_room_sub_agents_are_correct() -> None:
    """Test that writers_room has the correct sub-agents."""
    from backend.app.agents.workflows import writers_room

    agent_names = [agent.name for agent in writers_room.sub_agents]
    assert "researcher" in agent_names
    assert "screenwriter" in agent_names
    assert "critic" in agent_names
