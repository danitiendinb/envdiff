"""Normalize .env key/value pairs for consistent comparison and processing."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizeResult:
    normalized: Dict[str, str]
    changes: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changes)


def _normalize_key(key: str) -> str:
    """Strip whitespace and uppercase the key."""
    return key.strip().upper()


def _normalize_value(value: str) -> str:
    """Strip leading/trailing whitespace from value."""
    return value.strip()


def _normalize_boolean(value: str) -> str:
    """Normalize common boolean representations to 'true' or 'false'."""
    lower = value.lower()
    if lower in ("1", "yes", "on", "true"):
        return "true"
    if lower in ("0", "no", "off", "false"):
        return "false"
    return value


def normalize_env(
    env: Dict[str, str],
    uppercase_keys: bool = True,
    strip_values: bool = True,
    normalize_booleans: bool = False,
) -> NormalizeResult:
    """Return a normalized copy of *env* with a log of applied changes.

    Args:
        env: Raw key/value mapping.
        uppercase_keys: Convert all keys to uppercase.
        strip_values: Strip surrounding whitespace from values.
        normalize_booleans: Coerce truthy/falsy strings to 'true'/'false'.

    Returns:
        NormalizeResult with the cleaned mapping and a list of change descriptions.
    """
    normalized: Dict[str, str] = {}
    changes: List[str] = []

    for raw_key, raw_value in env.items():
        key = _normalize_key(raw_key) if uppercase_keys else raw_key.strip()
        value = _normalize_value(raw_value) if strip_values else raw_value

        if normalize_booleans:
            new_value = _normalize_boolean(value)
            if new_value != value:
                changes.append(f"{key}: boolean value '{value}' -> '{new_value}'")
            value = new_value

        if key != raw_key:
            changes.append(f"key '{raw_key}' -> '{key}'")
        if value != raw_value and not normalize_booleans:
            changes.append(f"{key}: value stripped of whitespace")

        normalized[key] = value

    return NormalizeResult(normalized=normalized, changes=changes)
