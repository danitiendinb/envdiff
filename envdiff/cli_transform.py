"""CLI sub-command: transform."""

from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.serializer import serialize_env
from envdiff.transformer import transform_env
from envdiff.transform_reporter import print_transform_report


def build_transform_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("transform", help="Apply transformations to a .env file")
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("--uppercase-keys", action="store_true", help="Uppercase all keys")
    p.add_argument("--strip-whitespace", action="store_true", help="Strip value whitespace")
    p.add_argument("--add-prefix", metavar="PREFIX", help="Add prefix to all keys")
    p.add_argument("--remove-prefix", metavar="PREFIX", help="Remove prefix from keys")
    p.add_argument("--mask-sensitive", action="store_true", help="Mask sensitive values")
    p.add_argument("--mask-value", default="***", help="Mask replacement string (default: ***)")
    p.add_argument("--output", metavar="FILE", help="Write result to file instead of stdout")
    p.add_argument("--report", action="store_true", help="Print a change report")
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    p.set_defaults(func=cmd_transform)


def cmd_transform(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error parsing file: {exc}", file=sys.stderr)
        return 1

    result = transform_env(
        env,
        uppercase_keys=args.uppercase_keys,
        strip_whitespace=args.strip_whitespace,
        add_prefix=args.add_prefix or None,
        remove_prefix=args.remove_prefix or None,
        mask_sensitive=args.mask_sensitive,
        mask_value=args.mask_value,
    )

    if args.report:
        print_transform_report(result, color=not args.no_color)
        print()

    serialized = serialize_env(result.transformed)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(serialized)
        except OSError as exc:
            print(f"Error writing output: {exc}", file=sys.stderr)
            return 1
    else:
        print(serialized)

    return 0
