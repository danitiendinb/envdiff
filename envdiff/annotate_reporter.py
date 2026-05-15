"""Reporter for AnnotateResult — formats annotation output for the terminal."""
from __future__ import annotations

import sys
from typing import IO

from envdiff.annotator import AnnotateResult


def _colorize(text: str, code: str) -> str:
    """Wrap *text* in an ANSI escape *code* when writing to a real TTY."""
    return f"\033[{code}m{text}\033[0m"


def format_annotate_report(result: AnnotateResult) -> str:
    """Return a human-readable string describing the annotation result."""
    lines: list[str] = []
    lines.append(_colorize("=== Annotation Report ===", "1"))
    lines.append(f"Total keys   : {len(result.annotated)}")
    lines.append(f"Annotated    : {result.annotation_count}")
    lines.append("")

    if not result.has_annotations:
        lines.append(_colorize("No annotations applied.", "2"))
        return "\n".join(lines)

    lines.append(_colorize("Annotated keys:", "1"))
    for key in sorted(result.comments):
        comment = result.comments[key]
        key_str = _colorize(key, "36")
        comment_str = _colorize(f"# {comment}", "33")
        lines.append(f"  {key_str}  {comment_str}")

    unannotated = sorted(k for k in result.annotated if k not in result.comments)
    if unannotated:
        lines.append("")
        lines.append(_colorize("Unannotated keys:", "2"))
        for key in unannotated:
            lines.append(f"  {_colorize(key, '37')}")

    return "\n".join(lines)


def print_annotate_report(result: AnnotateResult, *, file: IO[str] = sys.stdout) -> None:
    """Print the annotation report to *file* (default: stdout)."""
    print(format_annotate_report(result), file=file)
