"""Format and print tag reports."""

from __future__ import annotations

import sys
from typing import IO

from envdiff.tagger import TagResult

_COLORS = {
    "cyan": "\033[96m",
    "yellow": "\033[93m",
    "reset": "\033[0m",
}


def _colorize(text: str, color: str, *, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def format_tag_report(result: TagResult, *, use_color: bool = True) -> str:
    """Return a human-readable string summarising *result*."""
    lines: list[str] = []

    header = _colorize("=== Tag Report ===", "cyan", use_color=use_color)
    lines.append(header)
    lines.append(f"Total keys : {len(result.env)}")
    lines.append(f"Tags defined: {len(result.all_tags())}")
    lines.append("")

    if not result.all_tags():
        lines.append("No tags defined.")
        return "\n".join(lines)

    for tag in result.all_tags():
        keys = result.keys_for_tag(tag)
        label = _colorize(f"[{tag}]", "yellow", use_color=use_color)
        lines.append(f"{label} ({len(keys)} key{'s' if len(keys) != 1 else ''})")
        if keys:
            for key in keys:
                lines.append(f"    {key}")
        else:
            lines.append("    (none)")
        lines.append("")

    return "\n".join(lines).rstrip()


def print_tag_report(
    result: TagResult,
    *,
    use_color: bool = True,
    file: IO[str] | None = None,
) -> None:
    """Print the tag report to *file* (defaults to stdout)."""
    out = file or sys.stdout
    print(format_tag_report(result, use_color=use_color), file=out)
