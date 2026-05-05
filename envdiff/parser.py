"""Parser for .env files."""

import re
from typing import Dict, Optional, Tuple


ENV_LINE_RE = re.compile(
    r'^\s*(?:export\s+)?'
    r'([A-Za-z_][A-Za-z0-9_]*)'
    r'\s*=\s*'
    r'(.*?)\s*$'
)
COMMENT_RE = re.compile(r'^\s*#.*$')
BLANK_RE = re.compile(r'^\s*$')


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or \
           (value[0] == "'" and value[-1] == "'"):
            return value[1:-1]
    return value


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse the contents of a .env file into a key-value dictionary.

    Args:
        content: Raw string content of a .env file.

    Returns:
        Dictionary mapping variable names to their string values.

    Raises:
        ValueError: If a line is malformed (not a comment, blank, or valid assignment).
    """
    result: Dict[str, str] = {}
    for lineno, line in enumerate(content.splitlines(), start=1):
        if COMMENT_RE.match(line) or BLANK_RE.match(line):
            continue
        match = ENV_LINE_RE.match(line)
        if not match:
            raise ValueError(f"Malformed .env line {lineno}: {line!r}")
        key, raw_value = match.group(1), match.group(2)
        result[key] = _strip_quotes(raw_value)
    return result


def parse_env_file(path: str) -> Dict[str, str]:
    """Read and parse a .env file from disk.

    Args:
        path: Filesystem path to the .env file.

    Returns:
        Dictionary mapping variable names to their string values.
    """
    with open(path, "r", encoding="utf-8") as fh:
        return parse_env_string(fh.read())
