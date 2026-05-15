"""Human-readable report for SplitResult."""
from __future__ import annotations

from typing import Optional

from envdiff.splitter import SplitResult

_RESET = "\033[0m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_DIM = "\033[2m"


def _colorize(text: str, code: str, *, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_split_report(result: SplitResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = _colorize("=== Env Split Report ===", _BOLD, color=color)
    lines.append(header)
    lines.append(
        f"Total keys : {result.total_keys()}  "
        f"Partitions : {len(result.partitions)}"
    )
    lines.append("")

    for name, keys in result.partitions.items():
        section = _colorize(f"[{name}]  ({len(keys)} keys)", _CYAN, color=color)
        lines.append(section)
        if keys:
            for k in sorted(keys):
                lines.append(f"  {k}")
        else:
            lines.append(_colorize("  (empty)", _DIM, color=color))
        lines.append("")

    if result.unmatched:
        warn = _colorize(
            f"[unmatched]  ({len(result.unmatched)} keys)", _YELLOW, color=color
        )
        lines.append(warn)
        for k in sorted(result.unmatched):
            lines.append(f"  {k}")
    else:
        lines.append(_colorize("All keys matched a partition.", _DIM, color=color))

    return "\n".join(lines)


def print_split_report(result: SplitResult, *, color: bool = True) -> None:
    print(format_split_report(result, color=color))
