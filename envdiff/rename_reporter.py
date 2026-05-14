"""Format and print reports for RenameResult objects."""

import sys
from typing import TextIO

from envdiff.renamer import RenameResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_rename_report(result: RenameResult, *, color: bool = True) -> str:
    lines = []

    header = "=== Rename Report ==="
    lines.append(_colorize(header, "1") if color else header)

    if not result.renamed:
        msg = "No keys were renamed."
        lines.append(_colorize(msg, "33") if color else msg)
    else:
        lines.append(f"Renamed ({len(result.renamed)}):")
        for old, new in result.renamed:
            entry = f"  {old}  ->  {new}"
            lines.append(_colorize(entry, "32") if color else entry)

    if result.overwritten:
        lines.append(f"Overwritten ({len(result.overwritten)}):")
        for key in result.overwritten:
            entry = f"  {key}"
            lines.append(_colorize(entry, "33") if color else entry)

    if result.skipped:
        lines.append(f"Skipped / not found ({len(result.skipped)}):")
        for key in result.skipped:
            entry = f"  {key}"
            lines.append(_colorize(entry, "31") if color else entry)

    return "\n".join(lines)


def print_rename_report(
    result: RenameResult,
    *,
    color: bool = True,
    file: TextIO = sys.stdout,
) -> None:
    print(format_rename_report(result, color=color), file=file)
