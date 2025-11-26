"""Unit tests for agent tools."""

from typing import Any
from unittest.mock import Mock

import pytest


def test_wikipedia_search_returns_dict(mocker: Any) -> None:
    """Test that wikipedia_search returns success dict."""
    mocker.patch("wikipedia.summary", return_value="Ada Lovelace was a mathematician")

    from backend.app.agents.tools import wikipedia_search

    result = wikipedia_search(Mock(), "Ada Lovelace")

    assert result["status"] == "success"
    assert "results" in result
    assert "Ada Lovelace" in result["results"]


def test_wikipedia_search_handles_errors(mocker: Any) -> None:
    """Test that wikipedia_search handles errors gracefully."""
    mocker.patch("wikipedia.summary", side_effect=Exception("Not found"))

    from backend.app.agents.tools import wikipedia_search

    result = wikipedia_search(Mock(), "Invalid Topic 12345")

    assert result["status"] == "error"
    assert "error" in result


def test_wikipedia_search_with_empty_query(mocker: Any) -> None:
    """Test that wikipedia_search handles empty queries."""
    mocker.patch("wikipedia.summary", return_value="")

    from backend.app.agents.tools import wikipedia_search

    result = wikipedia_search(Mock(), "")

    assert "status" in result


def test_append_to_state_adds_content() -> None:
    """Test that append_to_state adds content to state."""
    from backend.app.agents.tools import append_to_state

    mock_context = Mock()
    mock_context.state = {}

    result = append_to_state(mock_context, "research", "test data")

    assert mock_context.state["research"] == ["test data"]
    assert result["status"] == "success"


def test_append_to_state_appends_to_existing() -> None:
    """Test that append_to_state appends to existing state."""
    from backend.app.agents.tools import append_to_state

    mock_context = Mock()
    mock_context.state = {"research": ["existing"]}

    append_to_state(mock_context, "research", "new")

    assert mock_context.state["research"] == ["existing", "new"]


def test_append_to_state_creates_new_key() -> None:
    """Test that append_to_state creates new key if not exists."""
    from backend.app.agents.tools import append_to_state

    mock_context = Mock()
    mock_context.state = {"other": ["data"]}

    append_to_state(mock_context, "research", "first")

    assert mock_context.state["research"] == ["first"]
    assert mock_context.state["other"] == ["data"]
