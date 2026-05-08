"""Format and print lint results for the terminal."""

from __future__ import annotations

import sys
from typing import TextIO

from envdiff.linter import LintResult

_COLORS = {
    "error": "\033[31m",
    "warning": "\033[33m",
    "info": "\033[36m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{_COLORS.get(color, '')}{text}{_COLORS['reset']}"


def format_lint_report(result: LintResult, use_color: bool = True) -> str:
    lines: list[str] = []

    if not result.has_issues:
        lines.append(_colorize("No lint issues found.", "info", use_color))
        return "\n".join(lines)

    severity_order = {"error": 0, "warning": 1, "info": 2}
    sorted_issues = sorted(result.issues, key=lambda i: (i.line, severity_order.get(i.severity, 9)))

    for issue in sorted_issues:
        prefix = _colorize(f"[{issue.severity.upper():7}]", issue.severity, use_color)
        code = _colorize(issue.code, "bold", use_color)
        lines.append(f"{prefix} {code}  {issue.message}")

    total = len(result.issues)
    errors = len(result.errors)
    warnings = len(result.warnings)
    summary = _colorize(
        f"\n{total} issue(s): {errors} error(s), {warnings} warning(s).",
        "bold",
        use_color,
    )
    lines.append(summary)
    return "\n".join(lines)


def print_lint_report(result: LintResult, use_color: bool = True, file: TextIO = sys.stdout) -> None:
    print(format_lint_report(result, use_color=use_color), file=file)
