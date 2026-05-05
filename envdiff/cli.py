"""CLI entry point for envdiff."""

import argparse
import json
import sys
from typing import Optional

from envdiff.parser import parse_env_file
from envdiff.differ import diff_envs
from envdiff.reporter import print_report
from envdiff.reconciler import generate_patch, apply_patch
from envdiff.validator import validate_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Diff and reconcile .env files across deployment environments.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # diff command
    diff_p = sub.add_parser("diff", help="Show differences between two .env files.")
    diff_p.add_argument("base", help="Base .env file")
    diff_p.add_argument("target", help="Target .env file")
    diff_p.add_argument("--no-color", action="store_true", help="Disable colored output")

    # patch command
    patch_p = sub.add_parser("patch", help="Apply a patch to reconcile a target .env file.")
    patch_p.add_argument("base", help="Base .env file")
    patch_p.add_argument("target", help="Target .env file to patch")
    patch_p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")

    # validate command
    validate_p = sub.add_parser("validate", help="Validate a .env file against a JSON schema.")
    validate_p.add_argument("env_file", help=".env file to validate")
    validate_p.add_argument("schema", help="JSON schema file (key -> type mapping)")
    validate_p.add_argument("--strict", action="store_true", help="Fail on unknown keys")

    return parser


def cmd_diff(args: argparse.Namespace) -> int:
    base = parse_env_file(args.base)
    target = parse_env_file(args.target)
    result = diff_envs(base, target)
    print_report(result, use_color=not args.no_color)
    return 0 if result.is_clean else 1


def cmd_patch(args: argparse.Namespace) -> int:
    base = parse_env_file(args.base)
    target = parse_env_file(args.target)
    patch = generate_patch(base, target)
    patched = apply_patch(target, patch)
    output_lines = [f"{k}={v}" for k, v in patched.items()]
    content = "\n".join(output_lines) + "\n"
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(content)
    else:
        sys.stdout.write(content)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    env = parse_env_file(args.env_file)
    with open(args.schema) as fh:
        schema = json.load(fh)
    result = validate_env(env, schema, strict=args.strict)
    if result.is_valid:
        print("Validation passed.")
        return 0
    if result.missing_required:
        print(f"Missing required keys: {', '.join(sorted(result.missing_required))}")
    if result.type_mismatches:
        for key, expected in sorted(result.type_mismatches.items()):
            print(f"Type mismatch: {key!r} expected {expected}")
    if result.unknown_keys:
        print(f"Unknown keys: {', '.join(sorted(result.unknown_keys))}")
    return 1


def main(argv: Optional[list] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {"diff": cmd_diff, "patch": cmd_patch, "validate": cmd_validate}
    sys.exit(handlers[args.command](args))


if __name__ == "__main__":
    main()
