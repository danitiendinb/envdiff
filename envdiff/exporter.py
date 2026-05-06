"""Export parsed env data to various formats (JSON, YAML, shell script)."""

import json
from typing import Dict, Optional


SUPPORTED_FORMATS = ("json", "yaml", "shell")


def export_as_json(env: Dict[str, str], indent: int = 2) -> str:
    """Serialize env dict to a JSON string."""
    return json.dumps(env, indent=indent, sort_keys=True)


def export_as_yaml(env: Dict[str, str]) -> str:
    """Serialize env dict to a simple YAML string (no external deps)."""
    if not env:
        return "{}"
    lines = []
    for key in sorted(env):
        value = env[key]
        # Quote values that contain special YAML characters
        if any(ch in value for ch in (':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', "'", '"')) or value == "":
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def export_as_shell(env: Dict[str, str]) -> str:
    """Serialize env dict as a shell export script."""
    if not env:
        return "#!/bin/sh"
    lines = ["#!/bin/sh"]
    for key in sorted(env):
        value = env[key].replace("'", "'\"'\"'")
        lines.append(f"export {key}='{value}'")
    return "\n".join(lines)


def export_env(
    env: Dict[str, str],
    fmt: str = "json",
    indent: int = 2,
) -> str:
    """Export env dict to the specified format.

    Args:
        env: Parsed environment dictionary.
        fmt: One of 'json', 'yaml', or 'shell'.
        indent: Indentation level for JSON output.

    Returns:
        Formatted string representation.

    Raises:
        ValueError: If an unsupported format is requested.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return export_as_json(env, indent=indent)
    if fmt == "yaml":
        return export_as_yaml(env)
    if fmt == "shell":
        return export_as_shell(env)
    raise ValueError(
        f"Unsupported export format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
    )
