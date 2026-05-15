"""CLI sub-command: side-by-side diff of two .env files."""
from __future__ import annotations
import argparse
import sys
from .parser import parse_env_file
from .differ3 import side_by_side_diff
from .side_by_side_reporter import print_side_by_side_report


def build_side_by_side_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "sidebyside",
        help="Show a side-by-side diff of two .env files.",
    )
    p.add_argument("left", help="Left (base) .env file")
    p.add_argument("right", help="Right (target) .env file")
    p.add_argument("--left-label", default=None, help="Label for the left column")
    p.add_argument("--right-label", default=None, help="Label for the right column")
    p.add_argument(
        "--col-width",
        type=int,
        default=30,
        help="Width of each value column (default: 30)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output",
    )
    p.set_defaults(func=cmd_side_by_side)


def cmd_side_by_side(args: argparse.Namespace) -> int:
    try:
        left_env = parse_env_file(args.left)
    except OSError as exc:
        print(f"error: cannot read '{args.left}': {exc}", file=sys.stderr)
        return 1

    try:
        right_env = parse_env_file(args.right)
    except OSError as exc:
        print(f"error: cannot read '{args.right}': {exc}", file=sys.stderr)
        return 1

    left_label = args.left_label or args.left
    right_label = args.right_label or args.right

    result = side_by_side_diff(
        left_env, right_env,
        left_label=left_label,
        right_label=right_label,
    )
    print_side_by_side_report(
        result,
        col_width=args.col_width,
        use_color=not args.no_color,
    )
    return 1 if result.has_changes else 0
