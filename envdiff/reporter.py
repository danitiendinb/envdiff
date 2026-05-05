"""Human-readable reporting for EnvDiffResult objects."""

from typing import TextIO
import sys

from envdiff.differ import EnvDiffResult


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if use_color:
        return f"{color}{text}{ANSI_RESET}"
    return text


def format_report(
    result: EnvDiffResult,
    source_label: str = "source",
    target_label: str = "target",
    use_color: bool = True,
) -> str:
    """Return a formatted diff report string for the given EnvDiffResult."""
    lines = []

    if not result.missing_keys and not result.extra_keys and not result.differing_keys:
        lines.append("No differences found.")
        return "\n".join(lines)

    if result.missing_keys:
        lines.append(
            _colorize(
                f"Keys in {source_label} but missing from {target_label} ({len(result.missing_keys)}):",
                ANSI_RED,
                use_color,
            )
        )
        for key in sorted(result.missing_keys):
            lines.append(f"  - {key}")

    if result.extra_keys:
        lines.append(
            _colorize(
                f"Keys in {target_label} but not in {source_label} ({len(result.extra_keys)}):",
                ANSI_GREEN,
                use_color,
            )
        )
        for key in sorted(result.extra_keys):
            lines.append(f"  + {key}")

    if result.differing_keys:
        lines.append(
            _colorize(
                f"Keys with differing values ({len(result.differing_keys)}):",
                ANSI_YELLOW,
                use_color,
            )
        )
        for key in sorted(result.differing_keys):
            src_val = result.source.get(key, "")
            tgt_val = result.target.get(key, "")
            lines.append(f"  ~ {key}")
            lines.append(f"      {source_label}: {src_val!r}")
            lines.append(f"      {target_label}: {tgt_val!r}")

    return "\n".join(lines)


def print_report(
    result: EnvDiffResult,
    source_label: str = "source",
    target_label: str = "target",
    use_color: bool = True,
    file: TextIO = sys.stdout,
) -> None:
    """Print a formatted diff report to the given file (default: stdout)."""
    report = format_report(result, source_label, target_label, use_color)
    print(report, file=file)
