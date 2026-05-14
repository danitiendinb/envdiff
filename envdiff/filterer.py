"""Filter .env entries by key pattern, prefix, or value condition."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, str]
    excluded: Dict[str, str]
    total: int

    @property
    def match_count(self) -> int:
        return len(self.matched)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)


def filter_by_pattern(env: Dict[str, str], pattern: str) -> FilterResult:
    """Keep only keys matching the given regex pattern."""
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise ValueError(f"Invalid pattern {pattern!r}: {exc}") from exc

    matched = {k: v for k, v in env.items() if compiled.search(k)}
    excluded = {k: v for k, v in env.items() if k not in matched}
    return FilterResult(matched=matched, excluded=excluded, total=len(env))


def filter_by_prefix(env: Dict[str, str], prefix: str) -> FilterResult:
    """Keep only keys that start with the given prefix (case-insensitive)."""
    upper_prefix = prefix.upper()
    matched = {k: v for k, v in env.items() if k.upper().startswith(upper_prefix)}
    excluded = {k: v for k, v in env.items() if k not in matched}
    return FilterResult(matched=matched, excluded=excluded, total=len(env))


def filter_empty_values(env: Dict[str, str]) -> FilterResult:
    """Keep only keys whose value is non-empty."""
    matched = {k: v for k, v in env.items() if v.strip() != ""}
    excluded = {k: v for k, v in env.items() if k not in matched}
    return FilterResult(matched=matched, excluded=excluded, total=len(env))


def filter_by_keys(env: Dict[str, str], keys: List[str]) -> FilterResult:
    """Keep only the explicitly listed keys."""
    key_set = set(keys)
    matched = {k: v for k, v in env.items() if k in key_set}
    excluded = {k: v for k, v in env.items() if k not in matched}
    return FilterResult(matched=matched, excluded=excluded, total=len(env))


def filter_env(
    env: Dict[str, str],
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
    keys: Optional[List[str]] = None,
    exclude_empty: bool = False,
) -> FilterResult:
    """Apply one or more filters sequentially; returns the combined result."""
    current = dict(env)
    total = len(env)

    if pattern is not None:
        current = filter_by_pattern(current, pattern).matched
    if prefix is not None:
        current = filter_by_prefix(current, prefix).matched
    if keys is not None:
        current = filter_by_keys(current, keys).matched
    if exclude_empty:
        current = filter_empty_values(current).matched

    excluded = {k: v for k, v in env.items() if k not in current}
    return FilterResult(matched=current, excluded=excluded, total=total)
