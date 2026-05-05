"""Command-line interface for envdiff."""

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.differ import diff_envs, has_differences
from envdiff.reporter import print_report
from envdiff.reconciler import generate_patch
from envdiff.serializer import serialize_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff and reconcile .env files across deployment environments.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # diff subcommand
    diff_cmd = subparsers.add_parser("diff", help="Show differences between two .env files.")
    diff_cmd.add_argument("source", help="Source .env file (reference)")
    diff_cmd.add_argument("target", help="Target .env file to compare")
    diff_cmd.add_argument("--no-color", action="store_true", help="Disable colored output")

    # patch subcommand
    patch_cmd = subparsers.add_parser(
        "patch", help="Generate a patch to bring target in line with source."
    )
    patch_cmd.add_argument("source", help="Source .env file (reference)")
    patch_cmd.add_argument("target", help="Target .env file to patch")
    patch_cmd.add_argument(
        "--fill",
        default="",
        metavar="VALUE",
        help="Fill value for missing keys (default: empty string)",
    )
    patch_cmd.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write patched output to FILE instead of stdout",
    )

    return parser


def cmd_diff(args: argparse.Namespace) -> int:
    source_env = parse_env_file(args.source)
    target_env = parse_env_file(args.target)
    result = diff_envs(source_env, target_env)
    print_report(
        result,
        source_label=args.source,
        target_label=args.target,
        use_color=not args.no_color,
    )
    return 1 if has_differences(result) else 0


def cmd_patch(args: argparse.Namespace) -> int:
    source_env = parse_env_file(args.source)
    target_env = parse_env_file(args.target)
    patch = generate_patch(source_env, target_env, fill_value=args.fill)
    patched = {**target_env, **patch}
    output = serialize_env(patched)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"Patched env written to {args.output}")
    else:
        print(output, end="")
    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "diff":
        return cmd_diff(args)
    if args.command == "patch":
        return cmd_patch(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
