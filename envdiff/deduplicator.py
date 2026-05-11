"""Detect and remove duplicate keys from a parsed env mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DeduplicateResult:
    """Result of a deduplication pass over an env mapping."""

    env: Dict[str, str]
    duplicates: Dict[str, List[str]]  # key -> list of all values seen

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    @property
    def duplicate_keys(self) -> List[str]:
        return sorted(self.duplicates.keys())


def find_duplicates(env_string: str) -> Dict[str, List[str]]:
    """Parse *env_string* line-by-line and collect every value seen per key.

    Returns a mapping of key -> [value1, value2, ...] for keys that appear
    more than once.  Keys that appear only once are omitted.
    """
    seen: Dict[str, List[str]] = {}
    for raw in env_string.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        seen.setdefault(key, []).append(value)

    return {k: v for k, v in seen.items() if len(v) > 1}


def deduplicate_env(
    env: Dict[str, str],
    env_string: str = "",
    *,
    keep: str = "last",
) -> DeduplicateResult:
    """Return a deduplicated copy of *env*.

    *env* is already a flat dict (last-write-wins from the parser), so
    deduplication here means detecting which keys had multiple definitions
    in the original *env_string* and recording them in the result.

    Parameters
    ----------
    env:
        Parsed env mapping (flat, no duplicates by definition).
    env_string:
        The raw source text used to detect duplicate definitions.
    keep:
        ``"last"`` (default) keeps the last occurrence; ``"first"`` keeps
        the first.  Affects the value stored in ``result.env`` for
        duplicate keys.
    """
    duplicates = find_duplicates(env_string) if env_string else {}

    clean: Dict[str, str] = dict(env)

    if keep == "first" and duplicates:
        for key, values in duplicates.items():
            clean[key] = values[0]

    return DeduplicateResult(env=clean, duplicates=duplicates)
