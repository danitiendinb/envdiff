"""Trim unused or redundant keys from an env dict based on a reference set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class TrimResult:
    """Result of a trim operation."""

    original: Dict[str, str]
    trimmed: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)

    @property
    def removal_count(self) -> int:
        return len(self.removed_keys)

    @property
    def has_removals(self) -> bool:
        return bool(self.removed_keys)


def trim_to_reference(
    env: Dict[str, str],
    reference: Set[str],
    *,
    ignore_case: bool = False,
) -> TrimResult:
    """Remove keys from *env* that are not present in *reference*.

    Args:
        env: The environment dict to trim.
        reference: Authoritative set of allowed key names.
        ignore_case: When True, key comparison is case-insensitive.

    Returns:
        A :class:`TrimResult` describing what was kept and what was removed.
    """
    if ignore_case:
        normalised_ref: Set[str] = {k.upper() for k in reference}
        kept = {k: v for k, v in env.items() if k.upper() in normalised_ref}
    else:
        kept = {k: v for k, v in env.items() if k in reference}

    removed = sorted(k for k in env if k not in kept)
    return TrimResult(original=dict(env), trimmed=kept, removed_keys=removed)


def trim_by_prefix(
    env: Dict[str, str],
    allowed_prefixes: List[str],
    *,
    delimiter: str = "_",
    ignore_case: bool = False,
) -> TrimResult:
    """Remove keys whose prefix is not in *allowed_prefixes*.

    Args:
        env: The environment dict to trim.
        allowed_prefixes: List of accepted key prefixes (e.g. ["DB", "APP"]).
        delimiter: Character used to split the prefix from the rest of the key.
        ignore_case: When True, prefix comparison is case-insensitive.

    Returns:
        A :class:`TrimResult` describing what was kept and what was removed.
    """
    norm = (lambda s: s.upper()) if ignore_case else (lambda s: s)
    normalised_prefixes = {norm(p) for p in allowed_prefixes}

    def _prefix(key: str) -> Optional[str]:
        if delimiter in key:
            return norm(key.split(delimiter, 1)[0])
        return None

    kept = {
        k: v
        for k, v in env.items()
        if _prefix(k) in normalised_prefixes
    }
    removed = sorted(k for k in env if k not in kept)
    return TrimResult(original=dict(env), trimmed=kept, removed_keys=removed)
