"""
Utility functions for the Merge Code Agent.
"""

import os
from typing import Dict, List, Any


def format_action_for_display(action: Dict[str, Any]) -> str:
    """
    Format an action for display to the user.

    Args:
        action: The action to format

    Returns:
        A formatted string representation of the action
    """
    action_type = action.get("action", "unknown")
    file_path = action.get("file_path", "unknown")

    if action_type == "create_file":
        return f"CREATE: {file_path}"
    elif action_type == "modify_file":
        return f"MODIFY: {file_path}"
    elif action_type == "delete_file":
        return f"DELETE: {file_path}"
    else:
        return f"UNKNOWN ACTION: {action_type} - {file_path}"


def format_actions_summary(actions: List[Dict[str, Any]]) -> str:
    """
    Format a summary of actions for display to the user.

    Args:
        actions: The list of actions to summarize

    Returns:
        A formatted summary of the actions
    """
    if not actions:
        return "No actions to perform."

    summary = "The following actions will be performed:\n\n"

    for i, action in enumerate(actions, 1):
        summary += f"{i}. {format_action_for_display(action)}\n"

    return summary


def get_action_preview(action: Dict[str, Any], max_lines: int = 10) -> str:
    """
    Get a preview of the action for display to the user.

    Args:
        action: The action to preview
        max_lines: Maximum number of lines to show in the preview

    Returns:
        A preview of the action
    """
    action_type = action.get("action", "unknown")
    file_path = action.get("file_path", "unknown")
    content = action.get("content", "")

    preview = f"Action: {action_type}\n"
    preview += f"File: {file_path}\n"

    if action_type in ["create_file", "modify_file"] and content:
        # Truncate content if it's too long
        lines = content.split("\n")
        if len(lines) > max_lines:
            displayed_lines = lines[:max_lines]
            displayed_lines.append(f"... ({len(lines) - max_lines} more lines)")
            content = "\n".join(displayed_lines)

        preview += f"\nContent Preview:\n{content}"

    return preview
