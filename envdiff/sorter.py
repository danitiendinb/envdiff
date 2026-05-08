"""Sort and group .env file keys by prefix, alphabet, or custom order."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    """Result of a sort operation on an env dict."""

    sorted_env: Dict[str, str]
    groups: Dict[str, List[str]]  # prefix -> list of keys

    def group_names(self) -> List[str]:
        """Return group names in the order they appear."""
        return list(self.groups.keys())


def _extract_prefix(key: str, separator: str = "_") -> str:
    """Return the first segment of a key before the separator, or '' if none."""
    parts = key.split(separator, 1)
    return parts[0] if len(parts) > 1 else ""


def sort_alphabetically(env: Dict[str, str]) -> SortResult:
    """Sort all keys alphabetically, placing unprefixed keys in group ''."""
    sorted_keys = sorted(env.keys())
    sorted_env = {k: env[k] for k in sorted_keys}
    groups: Dict[str, List[str]] = {}
    for k in sorted_keys:
        prefix = _extract_prefix(k)
        groups.setdefault(prefix, []).append(k)
    return SortResult(sorted_env=sorted_env, groups=groups)


def sort_by_prefix(
    env: Dict[str, str],
    prefix_order: Optional[List[str]] = None,
) -> SortResult:
    """
    Group keys by their prefix and sort within each group alphabetically.

    If *prefix_order* is provided, groups appear in that order first;
    remaining groups follow in alphabetical order.
    """
    groups: Dict[str, List[str]] = {}
    for k in sorted(env.keys()):
        prefix = _extract_prefix(k)
        groups.setdefault(prefix, []).append(k)

    if prefix_order:
        ordered_prefixes = list(prefix_order)
        for p in sorted(groups.keys()):
            if p not in ordered_prefixes:
                ordered_prefixes.append(p)
    else:
        ordered_prefixes = sorted(groups.keys())

    sorted_env: Dict[str, str] = {}
    ordered_groups: Dict[str, List[str]] = {}
    for prefix in ordered_prefixes:
        if prefix not in groups:
            continue
        keys = groups[prefix]
        ordered_groups[prefix] = keys
        for k in keys:
            sorted_env[k] = env[k]

    return SortResult(sorted_env=sorted_env, groups=ordered_groups)


def sort_env(
    env: Dict[str, str],
    mode: str = "alpha",
    prefix_order: Optional[List[str]] = None,
) -> SortResult:
    """
    Sort *env* using the given *mode*.

    Modes:
        ``alpha``  – simple alphabetical sort (default)
        ``prefix`` – group by key prefix, then alphabetical within each group
    """
    if mode == "prefix":
        return sort_by_prefix(env, prefix_order=prefix_order)
    return sort_alphabetically(env)
