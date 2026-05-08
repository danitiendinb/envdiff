"""Redact sensitive values from env dicts before display or export."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_FRAGMENTS = (
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "private", "auth", "credential", "cert", "private_key",
)

DEFAULT_MASK = "***REDACTED***"


@dataclass
class RedactResult:
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redaction_count(self) -> int:
        return len(self.redacted_keys)


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name suggests a sensitive value."""
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


def redact_env(
    env: Dict[str, str],
    mask: str = DEFAULT_MASK,
    extra_keys: Optional[List[str]] = None,
    preserve_length: bool = False,
) -> RedactResult:
    """Return a copy of *env* with sensitive values replaced by *mask*.

    Args:
        env: Mapping of environment variable names to values.
        mask: Replacement string for sensitive values.
        extra_keys: Additional key names (exact, case-insensitive) to redact.
        preserve_length: If True, replace each char with '*' instead of *mask*.
    """
    extra_lower = {k.lower() for k in (extra_keys or [])}
    result: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if is_sensitive_key(key) or key.lower() in extra_lower:
            replacement = "*" * len(value) if preserve_length else mask
            result[key] = replacement
            redacted_keys.append(key)
        else:
            result[key] = value

    return RedactResult(redacted=result, redacted_keys=sorted(redacted_keys))
