"""Profile .env files to extract statistics and patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

SENSITIVE_FRAGMENTS = ("password", "secret", "token", "key", "api", "auth", "private")


@dataclass
class ProfileResult:
    total_keys: int = 0
    empty_values: List[str] = field(default_factory=list)
    sensitive_keys: List[str] = field(default_factory=list)
    duplicate_values: Dict[str, List[str]] = field(default_factory=dict)
    longest_key: str = ""
    longest_value_key: str = ""


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(frag in lower for frag in SENSITIVE_FRAGMENTS)


def _find_duplicate_values(env: Dict[str, str]) -> Dict[str, List[str]]:
    value_map: Dict[str, List[str]] = {}
    for k, v in env.items():
        if v:
            value_map.setdefault(v, []).append(k)
    return {v: keys for v, keys in value_map.items() if len(keys) > 1}


def profile_env(env: Dict[str, str]) -> ProfileResult:
    """Analyse an env dict and return a ProfileResult with statistics."""
    result = ProfileResult(total_keys=len(env))

    for key, value in env.items():
        if not value:
            result.empty_values.append(key)
        if _is_sensitive(key):
            result.sensitive_keys.append(key)

    if env:
        result.longest_key = max(env.keys(), key=len)
        result.longest_value_key = max(env.keys(), key=lambda k: len(env[k]))

    result.duplicate_values = _find_duplicate_values(env)
    return result
