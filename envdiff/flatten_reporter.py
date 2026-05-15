"""Human-readable reporting for FlattenResult."""

from __future__ import annotations

import sys
from typing import IO

from envdiff.flattener import FlattenResult

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, *, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_flatten_report(result: FlattenResult, *, color: bool = False) -> str:
    """Return a formatted string summarising the flatten operation."""
    lines: list[str] = []

    header = _colorize("Flatten Report", _BOLD, color=color)
    lines.append(header)
    lines.append("-" * 40)

    sep_display = repr(result.separator)
    lines.append(f"Separator : {sep_display}")
    lines.append(f"Total keys: {result.key_count()}")

    if result.env:
        lines.append("")
        lines.append(_colorize("Flattened keys:", _GREEN, color=color))
        for key in sorted(result.env):
            lines.append(f"  {key}={result.env[key]!r}")
    else:
        lines.append(_colorize("  (no keys produced)", _YELLOW, color=color))

    if result.has_skipped():
        lines.append("")
        lines.append(_colorize("Skipped (max depth exceeded):", _RED, color=color))
        for path in result.skipped:
            lines.append(f"  {path}")

    return "\n".join(lines)


def print_flatten_report(
    result: FlattenResult,
    *,
    color: bool = True,
    file: IO[str] | None = None,
) -> None:
    """Print the flatten report to *file* (defaults to stdout)."""
    out = file or sys.stdout
    print(format_flatten_report(result, color=color), file=out)
