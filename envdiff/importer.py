"""Import env data from external formats (JSON, YAML-like, shell script)."""

import json
import re
from typing import Dict


def import_from_json(source: str) -> Dict[str, str]:
    """Parse a JSON string into an env dict.

    Only top-level string values are accepted; others are skipped.
    """
    data = json.loads(source)
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object/dict.")
    result: Dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[str(key)] = value
        else:
            result[str(key)] = str(value)
    return result


def import_from_yaml(source: str) -> Dict[str, str]:
    """Parse a minimal YAML string (key: value pairs only) into an env dict.

    Supports double-quoted values; ignores comments and blank lines.
    """
    result: Dict[str, str] = {}
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, _, raw_value = stripped.partition(":")
        key = key.strip()
        raw_value = raw_value.strip()
        # Strip surrounding double quotes if present
        if raw_value.startswith('"') and raw_value.endswith('"'):
            raw_value = raw_value[1:-1].replace('\\"', '"')
        result[key] = raw_value
    return result


def import_from_shell(source: str) -> Dict[str, str]:
    """Parse a shell export script into an env dict.

    Handles: export KEY='value', export KEY="value", export KEY=value
    """
    result: Dict[str, str] = {}
    pattern = re.compile(
        r"^(?:export\s+)?"
        r"([A-Za-z_][A-Za-z0-9_]*)="
        r"(?:'([^']*)'|\"([^\"]*)\"|([^\s#]*))",
        re.MULTILINE,
    )
    for match in pattern.finditer(source):
        key = match.group(1)
        value = next(v for v in match.groups()[1:] if v is not None)
        result[key] = value
    return result


def import_env(source: str, fmt: str = "json") -> Dict[str, str]:
    """Import env dict from a formatted string.

    Args:
        source: The formatted input string.
        fmt: One of 'json', 'yaml', or 'shell'.

    Returns:
        Parsed environment dictionary.

    Raises:
        ValueError: For unsupported formats or malformed input.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return import_from_json(source)
    if fmt == "yaml":
        return import_from_yaml(source)
    if fmt == "shell":
        return import_from_shell(source)
    raise ValueError(f"Unsupported import format '{fmt}'.")
