"""Scope filtering: restrict an env dict to a named scope defined by key prefixes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    """Result of scoping an env dict to a set of allowed prefixes."""
    scoped: Dict[str, str]
    excluded: Dict[str, str]
    scope_name: str
    prefixes: List[str]

    @property
    def included_count(self) -> int:
        return len(self.scoped)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)

    @property
    def has_excluded(self) -> bool:
        return bool(self.excluded)


def scope_env(
    env: Dict[str, str],
    prefixes: List[str],
    scope_name: str = "default",
    strip_prefix: bool = False,
    case_sensitive: bool = False,
) -> ScopeResult:
    """Filter *env* to only keys whose names start with one of *prefixes*.

    Args:
        env: Source environment mapping.
        prefixes: List of prefix strings to include.
        scope_name: Human-readable label for this scope.
        strip_prefix: When True, remove the matched prefix (and a trailing
            underscore if present) from the output key.
        case_sensitive: When False (default) matching ignores case.

    Returns:
        A :class:`ScopeResult` with the filtered and excluded mappings.
    """
    if not prefixes:
        return ScopeResult(
            scoped={},
            excluded=dict(env),
            scope_name=scope_name,
            prefixes=prefixes,
        )

    normalised_prefixes = [
        p if case_sensitive else p.upper() for p in prefixes
    ]

    scoped: Dict[str, str] = {}
    excluded: Dict[str, str] = {}

    for key, value in env.items():
        compare_key = key if case_sensitive else key.upper()
        matched_prefix: Optional[str] = None
        for raw_prefix, norm_prefix in zip(prefixes, normalised_prefixes):
            if compare_key.startswith(norm_prefix):
                matched_prefix = raw_prefix
                break

        if matched_prefix is None:
            excluded[key] = value
        else:
            if strip_prefix:
                stripped = key[len(matched_prefix):]
                if stripped.startswith("_"):
                    stripped = stripped[1:]
                out_key = stripped if stripped else key
            else:
                out_key = key
            scoped[out_key] = value

    return ScopeResult(
        scoped=scoped,
        excluded=excluded,
        scope_name=scope_name,
        prefixes=prefixes,
    )
