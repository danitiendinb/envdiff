"""Audit .env files for common security and hygiene issues."""

from dataclasses import dataclass, field
from typing import Dict, List

# Patterns that suggest a value might be a real secret placeholder or weak default
_WEAK_DEFAULTS = {"changeme", "secret", "password", "12345", "admin", "test", "example", "todo"}
_SENSITIVE_KEY_FRAGMENTS = ["password", "passwd", "secret", "token", "api_key", "private_key", "auth"]


@dataclass
class AuditIssue:
    key: str
    severity: str  # "warning" | "error"
    message: str


@dataclass
class AuditResult:
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def errors(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def _is_sensitive_key(key: str) -> bool:
    lower = key.lower()
    return any(fragment in lower for fragment in _SENSITIVE_KEY_FRAGMENTS)


def _check_empty_value(key: str, value: str) -> List[AuditIssue]:
    if value == "" and _is_sensitive_key(key):
        return [AuditIssue(key=key, severity="error",
                           message=f"Sensitive key '{key}' has an empty value.")]
    return []


def _check_weak_default(key: str, value: str) -> List[AuditIssue]:
    if _is_sensitive_key(key) and value.lower() in _WEAK_DEFAULTS:
        return [AuditIssue(key=key, severity="warning",
                           message=f"Key '{key}' appears to use a weak or placeholder value '{value}'.")]
    return []


def _check_whitespace_value(key: str, value: str) -> List[AuditIssue]:
    if value != value.strip():
        return [AuditIssue(key=key, severity="warning",
                           message=f"Key '{key}' has leading or trailing whitespace in its value.")]
    return []


def _check_key_naming(key: str) -> List[AuditIssue]:
    if not key.replace("_", "").isupper():
        return [AuditIssue(key=key, severity="warning",
                           message=f"Key '{key}' does not follow UPPER_SNAKE_CASE convention.")]
    return []


def audit_env(env: Dict[str, str]) -> AuditResult:
    """Run all audit checks against a parsed env dictionary."""
    result = AuditResult()
    for key, value in env.items():
        result.issues.extend(_check_key_naming(key))
        result.issues.extend(_check_empty_value(key, value))
        result.issues.extend(_check_weak_default(key, value))
        result.issues.extend(_check_whitespace_value(key, value))
    return result
