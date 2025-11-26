"""Agent tools for Wikipedia search and state management."""

from typing import Any

import wikipedia

from backend.app.agents.base import log_query, log_response


def wikipedia_search(tool_context: Any, query: str) -> dict[str, Any]:
    """
    Search Wikipedia for information on a topic.

    Args:
        tool_context: Context provided by the agent framework
        query: Search query string

    Returns:
        Dictionary with status and results/error

    Example:
        >>> result = wikipedia_search(context, "Ada Lovelace")
        >>> print(result["status"])
        'success'
    """
    log_query(f"Wikipedia search: {query}")

    try:
        summary = wikipedia.summary(query, sentences=3)
        result = {"status": "success", "results": summary}
        log_response(f"Wikipedia found: {len(summary)} characters")
        return result

    except Exception as e:
        error_msg = f"Wikipedia search failed: {str(e)}"
        log_response(error_msg)
        return {"status": "error", "error": error_msg}


def append_to_state(tool_context: Any, key: str, content: str) -> dict[str, str]:
    """
    Append content to the agent's state dictionary.

    Args:
        tool_context: Context provided by the agent framework
        key: State key to append to
        content: Content to append

    Returns:
        Dictionary with status

    Example:
        >>> result = append_to_state(context, "research", "Ada was born in 1815")
        >>> print(result["status"])
        'success'
    """
    if not hasattr(tool_context, "state") or tool_context.state is None:
        tool_context.state = {}

    if key not in tool_context.state:
        tool_context.state[key] = []

    tool_context.state[key].append(content)

    log_response(f"Appended to state[{key}]: {len(content)} characters")

    return {"status": "success"}
