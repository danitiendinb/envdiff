"""CLI subcommand: envdiff template — generate a .env template."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.parser import parse_env_file
from envdiff.templater import build_template, render_template, template_from_keys


def build_template_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "template",
        help="Generate a .env template from an existing env file or key list.",
    )
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--from-file",
        metavar="FILE",
        help="Derive template from an existing .env file.",
    )
    source.add_argument(
        "--from-keys",
        metavar="KEY",
        nargs="+",
        help="Build a blank template from explicit key names.",
    )
    p.add_argument(
        "--no-redact",
        action="store_true",
        default=False,
        help="Do not redact sensitive values (default: redact).",
    )
    p.add_argument(
        "--placeholder",
        default="",
        metavar="TEXT",
        help="Placeholder text for redacted / blank values.",
    )
    p.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        default="-",
        help="Output file path (default: stdout).",
    )
    p.set_defaults(func=cmd_template)


def cmd_template(args: argparse.Namespace) -> int:
    if args.from_file:
        try:
            env = parse_env_file(args.from_file)
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        tmpl = build_template(
            env,
            redact_sensitive=not args.no_redact,
            placeholder=args.placeholder,
        )
    else:
        tmpl = template_from_keys(
            args.from_keys,
            placeholder=args.placeholder,
        )

    rendered = render_template(tmpl)

    if args.output == "-":
        sys.stdout.write(rendered)
    else:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(rendered)
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    return 0
