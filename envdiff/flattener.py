"""Flatten nested env-like structures into a single-level dict of KEY=value pairs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FlattenResult:
    """Result of a flatten operation."""

    env: Dict[str, str]
    skipped: List[str] = field(default_factory=list)
    separator: str = "__"

    def key_count(self) -> int:
        return len(self.env)

    def has_skipped(self) -> bool:
        return bool(self.skipped)


def _flatten_dict(
    obj: Any,
    parent_key: str,
    separator: str,
    result: Dict[str, str],
    skipped: List[str],
    max_depth: int,
    current_depth: int,
) -> None:
    """Recursively walk *obj* and populate *result* with flattened keys."""
    if current_depth > max_depth:
        skipped.append(parent_key)
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{separator}{k}" if parent_key else str(k)
            _flatten_dict(v, new_key, separator, result, skipped, max_depth, current_depth + 1)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
            _flatten_dict(v, new_key, separator, result, skipped, max_depth, current_depth + 1)
    elif obj is None:
        result[parent_key.upper()] = ""
    elif isinstance(obj, bool):
        result[parent_key.upper()] = "true" if obj else "false"
    else:
        result[parent_key.upper()] = str(obj)


def flatten_env(
    nested: Dict[str, Any],
    separator: str = "__",
    prefix: Optional[str] = None,
    max_depth: int = 10,
) -> FlattenResult:
    """Flatten a nested mapping into a flat env dict.

    Args:
        nested:    Arbitrarily nested dict to flatten.
        separator: String used to join key segments (default ``__``).
        prefix:    Optional prefix prepended to every top-level key.
        max_depth: Maximum nesting depth before a key is skipped.

    Returns:
        A :class:`FlattenResult` with the flattened env and any skipped paths.
    """
    result: Dict[str, str] = {}
    skipped: List[str] = []

    for k, v in nested.items():
        root = f"{prefix}{separator}{k}" if prefix else str(k)
        _flatten_dict(v, root, separator, result, skipped, max_depth, current_depth=1)

    return FlattenResult(env=result, skipped=skipped, separator=separator)
