"""Format and print TransformResult reports."""

from __future__ import annotations

import sys
from typing import IO

from envdiff.transformer import TransformResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_transform_report(result: TransformResult, *, color: bool = True) -> str:
    lines = []

    header = "Transform Report"
    lines.append(_colorize(header, "1;34") if color else header)
    lines.append("")

    applied_label = "Transformations applied:"
    lines.append(_colorize(applied_label, "1") if color else applied_label)
    if result.applied:
        for t in result.applied:
            lines.append(f"  - {t}")
    else:
        lines.append("  (none)")
    lines.append("")

    changed = result.changed_keys
    summary = f"Changed keys: {len(changed)} / {len(result.transformed)}"
    lines.append(_colorize(summary, "1") if color else summary)

    if changed:
        lines.append("")
        for k in sorted(changed):
            old_val = result.original.get(k, "<missing>")
            new_val = result.transformed[k]
            old_str = _colorize(f"- {k}={old_val}", "31") if color else f"- {k}={old_val}"
            new_str = _colorize(f"+ {k}={new_val}", "32") if color else f"+ {k}={new_val}"
            lines.append(old_str)
            lines.append(new_str)
    else:
        no_change = "  No values changed."
        lines.append(_colorize(no_change, "2") if color else no_change)

    return "\n".join(lines)


def print_transform_report(
    result: TransformResult,
    *,
    color: bool = True,
    file: IO[str] = sys.stdout,
) -> None:
    print(format_transform_report(result, color=color), file=file)
