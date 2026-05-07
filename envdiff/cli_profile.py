"""CLI helpers for the 'profile' subcommand."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.parser import parse_env_file
from envdiff.profiler import profile_env
from envdiff.profile_reporter import print_profile_report


def build_profile_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "profile",
        help="Display statistics and patterns for one or more .env files.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to profile")
    p.add_argument("--no-color", action="store_true", help="Disable coloured output")


def cmd_profile(args: argparse.Namespace) -> int:
    """Execute the profile subcommand; returns an exit code."""
    exit_code = 0
    for path in args.files:
        try:
            env = parse_env_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            exit_code = 1
            continue
        except OSError as exc:
            print(f"error: could not read {path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        print(f"\n=== {path} ===")
        result = profile_env(env)
        print_profile_report(result, color=not args.no_color)

    return exit_code
