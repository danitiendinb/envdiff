"""Lint .env files for common style and correctness issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "api_key", "private")


@dataclass
class LintIssue:
    line: int
    key: str
    code: str
    message: str
    severity: str  # 'error' | 'warning' | 'info'


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)


def _is_sensitive_key(key: str) -> bool:
    return any(frag in key.lower() for frag in _SENSITIVE_FRAGMENTS)


def lint_env_string(source: str) -> LintResult:
    """Lint raw .env source text line by line."""
    result = LintResult()
    seen_keys: Dict[str, int] = {}

    for lineno, raw in enumerate(source.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        stripped = line.removeprefix("export ").strip()
        if "=" not in stripped:
            result.issues.append(
                LintIssue(lineno, "", "E001", f"Line {lineno}: missing '=' separator", "error")
            )
            continue

        key, _, value = stripped.partition("=")
        key = key.strip()

        if not key:
            result.issues.append(
                LintIssue(lineno, key, "E002", f"Line {lineno}: empty key", "error")
            )
            continue

        if key != key.upper():
            result.issues.append(
                LintIssue(lineno, key, "W001", f"'{key}' is not uppercase", "warning")
            )

        if " " in key:
            result.issues.append(
                LintIssue(lineno, key, "E003", f"'{key}' contains whitespace", "error")
            )

        if key in seen_keys:
            result.issues.append(
                LintIssue(
                    lineno, key, "W002",
                    f"'{key}' duplicated (first on line {seen_keys[key]})",
                    "warning",
                )
            )
        else:
            seen_keys[key] = lineno

        if value == "" and not _is_sensitive_key(key):
            result.issues.append(
                LintIssue(lineno, key, "I001", f"'{key}' has an empty value", "info")
            )

    return result
