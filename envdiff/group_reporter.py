"""Render GroupResult objects for terminal output."""
from __future__ import annotations

import sys
from typing import TextIO

from .grouper import GroupResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_DIM = "\033[2m"


def _colorize(text: str, code: str, *, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{code}{text}{_RESET}"


def format_group_report(result: GroupResult, *, use_color: bool = False) -> str:
    lines: list[str] = []

    header = _colorize("Grouped Environment Variables", _BOLD, use_color=use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not result.groups and not result.ungrouped:
        lines.append(_colorize("(no keys)", _DIM, use_color=use_color))
        return "\n".join(lines)

    for group_name in result.group_names():
        label = _colorize(f"[{group_name}]", _CYAN, use_color=use_color)
        lines.append(label)
        for key, value in sorted(result.groups[group_name].items()):
            lines.append(f"  {key}={value}")

    if result.ungrouped:
        label = _colorize("[ungrouped]", _YELLOW, use_color=use_color)
        lines.append(label)
        for key, value in sorted(result.ungrouped.items()):
            lines.append(f"  {key}={value}")

    lines.append("-" * 40)
    total = result.total_groups()
    ungrouped_count = len(result.ungrouped)
    summary = (
        f"{total} group(s)  |  {ungrouped_count} ungrouped key(s)"
    )
    lines.append(_colorize(summary, _DIM, use_color=use_color))
    return "\n".join(lines)


def print_group_report(
    result: GroupResult,
    *,
    use_color: bool = True,
    file: TextIO = sys.stdout,
) -> None:
    print(format_group_report(result, use_color=use_color), file=file)
