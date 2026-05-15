"""CLI sub-command: envdiff unified-diff — show a unified diff between two .env files."""
from __future__ import annotations

import argparse
import sys

from envdiff.differ2 import unified_diff
from envdiff.parser import parse_env_file
from envdiff.unified_diff_reporter import print_unified_diff_report


def build_unified_diff_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "unified-diff",
        help="Show a unified diff between two .env files.",
    )
    p.add_argument("file_a", help="Base .env file (left side).")
    p.add_argument("file_b", help="Target .env file (right side).")
    p.add_argument(
        "--no-context",
        action="store_true",
        default=False,
        help="Omit unchanged keys from the output.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    p.add_argument(
        "--label-a",
        default=None,
        help="Override the label shown for file_a (defaults to the filename).",
    )
    p.add_argument(
        "--label-b",
        default=None,
        help="Override the label shown for file_b (defaults to the filename).",
    )
    p.set_defaults(func=cmd_unified_diff)


def cmd_unified_diff(args: argparse.Namespace) -> int:
    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except FileNotFoundError as exc:
        print(f"envdiff: error: {exc}", file=sys.stderr)
        return 1

    label_a = args.label_a or args.file_a
    label_b = args.label_b or args.file_b
    context = not args.no_context
    use_color = not args.no_color

    result = unified_diff(env_a, env_b, label_a=label_a, label_b=label_b, context=context)
    print_unified_diff_report(result, use_color=use_color)

    return 1 if result.has_changes else 0
