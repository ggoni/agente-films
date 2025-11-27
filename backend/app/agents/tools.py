"""Agent tools for Wikipedia search and state management."""

from typing import Any

import wikipedia

from backend.app.agents.base import log_query, log_response


def wikipedia_search(_tool_context: Any, query: str) -> dict[str, Any]:
    """
    Search Wikipedia for information on a topic.

    Args:
        _tool_context: Context provided by the agent framework (unused)
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


def write_file(_tool_context: Any, filename: str, directory: str, content: str) -> dict[str, Any]:
    """
    Write content to a file in the specified directory.

    Args:
        _tool_context: Context provided by the agent framework (unused)
        filename: Base filename (without extension, .txt will be added)
        directory: Directory path to write file to
        content: Content to write to the file

    Returns:
        Dictionary with status and file path or error

    Example:
        >>> result = write_file(context, "pitch", "/tmp", "Film concept...")
        >>> print(result["status"])
        'success'
    """
    from pathlib import Path

    log_query(f"Writing file: {filename} to {directory}")

    try:
        dir_path = Path(directory)
        file_path = dir_path / f"{filename}.txt"

        # Create directory if it doesn't exist
        dir_path.mkdir(parents=True, exist_ok=True)

        # Write content to file
        file_path.write_text(content, encoding="utf-8")

        result = {"status": "success", "path": str(file_path)}
        log_response(f"File written: {file_path} ({len(content)} characters)")
        return result

    except Exception as e:
        error_msg = f"File write failed: {str(e)}"
        log_response(error_msg)
        return {"status": "error", "error": error_msg}
