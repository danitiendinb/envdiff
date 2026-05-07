"""Format and print CompareResult objects for human-readable output."""

from typing import List

from envdiff.comparator import CompareResult, EnvChange

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _colorize(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_compare_report(result: CompareResult, use_color: bool = False) -> str:
    lines: List[str] = []

    header = f"Comparing {result.source_label!r} → {result.target_label!r}"
    lines.append(_colorize(header, _BOLD, use_color))
    lines.append("")

    if not result.has_changes:
        lines.append("  No changes detected.")
        return "\n".join(lines)

    if result.added:
        lines.append(_colorize(f"  Added ({len(result.added)}):", _GREEN, use_color))
        for c in result.added:
            lines.append(_colorize(f"    + {c.key}={c.new_value}", _GREEN, use_color))

    if result.removed:
        lines.append(_colorize(f"  Removed ({len(result.removed)}):", _RED, use_color))
        for c in result.removed:
            lines.append(_colorize(f"    - {c.key}={c.old_value}", _RED, use_color))

    if result.modified:
        lines.append(_colorize(f"  Modified ({len(result.modified)}):", _YELLOW, use_color))
        for c in result.modified:
            lines.append(_colorize(f"    ~ {c.key}: {c.old_value!r} → {c.new_value!r}", _YELLOW, use_color))

    return "\n".join(lines)


def print_compare_report(result: CompareResult, use_color: bool = False) -> None:
    print(format_compare_report(result, use_color=use_color))
