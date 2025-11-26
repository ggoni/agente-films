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


def test_preproduction_team_exists() -> None:
    """Test that preproduction_team workflow is defined."""
    from backend.app.agents.workflows import preproduction_team

    assert preproduction_team is not None


def test_preproduction_team_has_name() -> None:
    """Test that preproduction_team has correct name."""
    from backend.app.agents.workflows import preproduction_team

    assert preproduction_team.name == "preproduction_team"


def test_preproduction_team_has_two_agents() -> None:
    """Test that preproduction_team has 2 sub-agents."""
    from backend.app.agents.workflows import preproduction_team

    assert hasattr(preproduction_team, "sub_agents")
    assert isinstance(preproduction_team.sub_agents, list)
    assert len(preproduction_team.sub_agents) == 2


def test_preproduction_team_sub_agents_are_correct() -> None:
    """Test that preproduction_team has correct sub-agents."""
    from backend.app.agents.workflows import preproduction_team

    agent_names = [a.name for a in preproduction_team.sub_agents]
    assert "box_office_researcher" in agent_names
    assert "casting_agent" in agent_names


def test_film_concept_team_exists() -> None:
    """Test that film_concept_team workflow exists."""
    from backend.app.agents.workflows import film_concept_team

    assert film_concept_team is not None


def test_film_concept_team_is_sequential() -> None:
    """Test that film_concept_team is a SequentialAgentConfig."""
    from backend.app.agents.workflows import SequentialAgentConfig, film_concept_team

    assert isinstance(film_concept_team, SequentialAgentConfig)


def test_film_concept_team_has_name() -> None:
    """Test that film_concept_team has correct name."""
    from backend.app.agents.workflows import film_concept_team

    assert film_concept_team.name == "film_concept_team"


def test_film_concept_team_has_description() -> None:
    """Test that film_concept_team has description."""
    from backend.app.agents.workflows import film_concept_team

    assert hasattr(film_concept_team, "description")
    assert len(film_concept_team.description) > 0


def test_film_concept_team_has_three_agents() -> None:
    """Test that film_concept_team has three sub-agents."""
    from backend.app.agents.workflows import film_concept_team

    assert len(film_concept_team.sub_agents) == 3


def test_film_concept_team_sub_agents_in_order() -> None:
    """Test that film_concept_team sub-agents are in correct order."""
    from backend.app.agents.workflows import film_concept_team

    agent_names = []
    for a in film_concept_team.sub_agents:
        # Handle both object-based agents (workflows) and dict-based agents (file_writer)
        if isinstance(a, dict):
            agent_names.append(a["name"])
        else:
            agent_names.append(a.name)
    
    assert agent_names == ["writers_room", "preproduction_team", "file_writer"]

