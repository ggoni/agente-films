"""Unit tests for base agent utilities."""

import logging

import pytest

from backend.app.agents.base import get_model_name, log_query, log_response


def test_get_model_name_returns_string() -> None:
    """Test that get_model_name returns a valid model string."""
    model = get_model_name()
    assert isinstance(model, str)
    assert len(model) > 0


def test_get_model_name_is_consistent() -> None:
    """Test that get_model_name returns the same value consistently."""
    model1 = get_model_name()
    model2 = get_model_name()
    assert model1 == model2


def test_log_query_accepts_string(caplog: pytest.LogCaptureFixture) -> None:
    """Test that log_query logs the query message."""
    with caplog.at_level(logging.INFO):
        log_query("test query")
        assert "test query" in caplog.text
        assert "Query" in caplog.text


def test_log_response_accepts_string(caplog: pytest.LogCaptureFixture) -> None:
    """Test that log_response logs the response message."""
    with caplog.at_level(logging.INFO):
        log_response("test response")
        assert "test response" in caplog.text
        assert "Response" in caplog.text


def test_log_query_with_empty_string(caplog: pytest.LogCaptureFixture) -> None:
    """Test that log_query handles empty strings."""
    with caplog.at_level(logging.INFO):
        log_query("")
        assert "Query" in caplog.text


def test_log_response_with_multiline(caplog: pytest.LogCaptureFixture) -> None:
    """Test that log_response handles multiline strings."""
    with caplog.at_level(logging.INFO):
        log_response("line1\nline2\nline3")
        assert "line1" in caplog.text or "Response" in caplog.text
