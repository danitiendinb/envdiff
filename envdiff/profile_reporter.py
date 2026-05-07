"""Format and print ProfileResult summaries."""

from __future__ import annotations

from typing import Optional

from envdiff.profiler import ProfileResult


def _section(title: str) -> str:
    return f"\n--- {title} ---"


def format_profile_report(result: ProfileResult, color: bool = False) -> str:
    lines = []

    def _warn(text: str) -> str:
        return f"\033[33m{text}\033[0m" if color else text

    def _info(text: str) -> str:
        return f"\033[36m{text}\033[0m" if color else text

    lines.append(_section("Env Profile Summary"))
    lines.append(f"  Total keys      : {result.total_keys}")
    lines.append(f"  Longest key     : {result.longest_key or '(none)'}")
    lines.append(f"  Key w/ longest value: {result.longest_value_key or '(none)'}")

    lines.append(_section("Empty Values"))
    if result.empty_values:
        for k in sorted(result.empty_values):
            lines.append(f"  {_warn(k)} = (empty)")
    else:
        lines.append("  (none)")

    lines.append(_section("Sensitive Keys"))
    if result.sensitive_keys:
        for k in sorted(result.sensitive_keys):
            lines.append(f"  {_warn(k)}")
    else:
        lines.append("  (none)")

    lines.append(_section("Duplicate Values"))
    if result.duplicate_values:
        for val, keys in result.duplicate_values.items():
            short_val = val[:30] + "..." if len(val) > 30 else val
            lines.append(f"  '{_info(short_val)}' shared by: {', '.join(sorted(keys))}")
    else:
        lines.append("  (none)")

    return "\n".join(lines)


def print_profile_report(result: ProfileResult, color: bool = True) -> None:
    print(format_profile_report(result, color=color))
