"""Reporter for interpolation results."""

from __future__ import annotations

from typing import List

from .interpolator import InterpolateResult

_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, *, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_interpolate_report(
    result: InterpolateResult, *, color: bool = True
) -> str:
    lines: List[str] = []

    header = _colorize("Interpolation Report", _BOLD, color=color)
    lines.append(header)
    lines.append("-" * 40)

    expanded_count = len(result.expanded)
    unresolved_count = len(result.unresolved)

    lines.append(f"Keys expanded : {expanded_count}")
    lines.append(f"Unresolved    : {unresolved_count}")

    if result.expanded:
        lines.append("")
        lines.append(_colorize("Expanded keys:", _GREEN, color=color))
        for key, new_val in sorted(result.expanded.items()):
            lines.append(f"  {key} = {new_val}")

    if result.unresolved:
        lines.append("")
        lines.append(_colorize("Unresolved references:", _YELLOW, color=color))
        for key in sorted(result.unresolved):
            lines.append(
                f"  {_colorize(key, _RED, color=color)}"
                f" = {result.env[key]}"
            )

    if not result.expanded and not result.unresolved:
        lines.append("")
        lines.append(
            _colorize("No interpolation needed — all values are literal.", _GREEN, color=color)
        )

    return "\n".join(lines)


def print_interpolate_report(
    result: InterpolateResult, *, color: bool = True
) -> None:
    print(format_interpolate_report(result, color=color))
