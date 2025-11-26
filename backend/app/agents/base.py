"""Base agent utilities and shared configuration."""

import logging
from typing import Any

# Configure logger
logger = logging.getLogger(__name__)


def get_model_name() -> str:
    """
    Get the default model name for agents.

    Returns:
        str: Model name for LLM (defaults to Gemini Pro)

    Example:
        >>> model = get_model_name()
        >>> print(model)
        'gemini-2.0-flash-exp'
    """
    return "gemini-2.0-flash-exp"


def log_query(query: str) -> None:
    """
    Log an agent query for debugging and monitoring.

    Args:
        query: The query string sent to the agent

    Example:
        >>> log_query("What is the historical context?")
    """
    logger.info(f"Query: {query}")


def log_response(response: str) -> None:
    """
    Log an agent response for debugging and monitoring.

    Args:
        response: The response string from the agent

    Example:
        >>> log_response("Historical context includes...")
    """
    logger.info(f"Response: {response}")
