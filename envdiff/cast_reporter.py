"""Reporter for CastResult output."""
from __future__ import annotations

from typing import List

from envdiff.caster import CastResult

_COLORS = {
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def _colorize(text: str, color: str) -> str:
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def format_cast_report(result: CastResult, *, color: bool = True) -> str:
    lines: List[str] = []

    header = "=== Cast Report ==="
    lines.append(_colorize(header, "bold") if color else header)
    lines.append(f"Total keys : {len(result.original)}")
    lines.append(f"Cast       : {result.cast_count}")
    lines.append(f"Skipped    : {len(result.skipped)}")
    lines.append("")

    changed = [
        k for k in result.casted
        if result.casted[k] != result.original.get(k)
    ]
    if changed:
        section = "Type changes:"
        lines.append(_colorize(section, "cyan") if color else section)
        for k in sorted(changed):
            orig = repr(result.original[k])
            new = repr(result.casted[k])
            type_name = type(result.casted[k]).__name__
            line = f"  {k}: {orig} -> {new}  ({type_name})"
            lines.append(_colorize(line, "green") if color else line)
    else:
        lines.append("No type changes — all values remain as strings.")

    if result.skipped:
        lines.append("")
        skipped_hdr = "Skipped keys (kept as string):"
        lines.append(_colorize(skipped_hdr, "yellow") if color else skipped_hdr)
        for k in sorted(result.skipped):
            lines.append(f"  {k}")

    return "\n".join(lines)


def print_cast_report(result: CastResult, *, color: bool = True) -> None:
    print(format_cast_report(result, color=color))
