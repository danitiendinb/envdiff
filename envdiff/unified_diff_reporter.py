"""Human-readable reporter for UnifiedDiffResult."""
from __future__ import annotations

import sys
from typing import TextIO

from envdiff.differ2 import DiffLine, UnifiedDiffResult

_COLORS = {
    "reset": "\033[0m",
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
}


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def _format_line(line: DiffLine, use_color: bool) -> str:
    sym = line.symbol
    if line.kind == "context":
        return f"  {line.key}={line.old_value}"
    if line.kind == "added":
        val = f"{line.key}={line.new_value}"
        return _colorize(f"+ {val}", "green", use_color)
    if line.kind == "removed":
        val = f"{line.key}={line.old_value}"
        return _colorize(f"- {val}", "red", use_color)
    if line.kind == "changed":
        old = _colorize(f"- {line.key}={line.old_value}", "red", use_color)
        new = _colorize(f"+ {line.key}={line.new_value}", "green", use_color)
        return f"{old}\n{new}"
    return f"{sym} {line.key}"


def format_unified_diff_report(result: UnifiedDiffResult, use_color: bool = True) -> str:
    parts: list[str] = []
    header = f"--- {result.label_a}\n+++ {result.label_b}"
    parts.append(_colorize(header, "bold", use_color))

    if not result.has_changes:
        parts.append(_colorize("(no differences)", "cyan", use_color))
        return "\n".join(parts)

    for line in result.lines:
        parts.append(_format_line(line, use_color))

    summary_parts = []
    if result.added_keys:
        summary_parts.append(_colorize(f"+{len(result.added_keys)} added", "green", use_color))
    if result.removed_keys:
        summary_parts.append(_colorize(f"-{len(result.removed_keys)} removed", "red", use_color))
    if result.changed_keys:
        summary_parts.append(_colorize(f"~{len(result.changed_keys)} changed", "yellow", use_color))
    if summary_parts:
        parts.append("  " + "  ".join(summary_parts))

    return "\n".join(parts)


def print_unified_diff_report(
    result: UnifiedDiffResult,
    use_color: bool = True,
    file: TextIO = sys.stdout,
) -> None:
    print(format_unified_diff_report(result, use_color=use_color), file=file)
