"""Format and print side-by-side diff reports."""
from __future__ import annotations
from typing import Optional
from .differ3 import SideBySideResult, SideBySideLine

_COLORS = {
    "added": "\033[32m",
    "removed": "\033[31m",
    "changed": "\033[33m",
    "same": "",
    "reset": "\033[0m",
    "bold": "\033[1m",
}

_STATUS_SYMBOL = {
    "added": "+",
    "removed": "-",
    "changed": "~",
    "same": " ",
}


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def _pad(value: Optional[str], width: int) -> str:
    s = "" if value is None else value
    return s.ljust(width)


def format_side_by_side_report(
    result: SideBySideResult,
    col_width: int = 30,
    use_color: bool = True,
) -> str:
    lines: list[str] = []
    bold = _COLORS["bold"] if use_color else ""
    reset = _COLORS["reset"] if use_color else ""
    header = (
        f"{bold}{'KEY':<20}  "
        f"{result.left_label:<{col_width}}  "
        f"{result.right_label:<{col_width}}{reset}"
    )
    lines.append(header)
    lines.append("-" * (20 + 2 + col_width + 2 + col_width))

    if not result.lines:
        lines.append("  (no keys)")
        return "\n".join(lines)

    for ln in result.lines:
        sym = _STATUS_SYMBOL[ln.status]
        left_str = _pad(ln.left_value, col_width)
        right_str = _pad(ln.right_value, col_width)
        row = f"{sym} {ln.key:<20}  {left_str}  {right_str}"
        lines.append(_colorize(row, ln.status, use_color))

    changed = len(result.changed_keys)
    added = len(result.added_keys)
    removed = len(result.removed_keys)
    lines.append("")
    summary = f"Summary: {changed} changed, {added} added, {removed} removed"
    lines.append(_colorize(summary, "bold" if result.has_changes else "same", use_color))
    return "\n".join(lines)


def print_side_by_side_report(
    result: SideBySideResult,
    col_width: int = 30,
    use_color: bool = True,
) -> None:
    print(format_side_by_side_report(result, col_width=col_width, use_color=use_color))
