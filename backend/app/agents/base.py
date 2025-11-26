"""Base agent utilities and shared configuration."""

import logging
import os
from typing import Any

from backend.app.config import Settings

# Configure logger
logger = logging.getLogger(__name__)

# Initialize settings
_settings = Settings()


def get_model_name() -> str:
    """
    Get the default model name for agents from environment or config.

    Returns:
        str: Model name for LLM from MODEL env var or config

    Example:
        >>> model = get_model_name()
        >>> print(model)
        'gemini-2.5-flash'
    """
    return os.getenv("MODEL", _settings.MODEL)


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
