"""Clone an env dict with optional key remapping, filtering, and value overrides."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CloneResult:
    """Result of a clone operation."""

    env: Dict[str, str]
    remapped: List[str] = field(default_factory=list)
    overridden: List[str] = field(default_factory=list)
    dropped: List[str] = field(default_factory=list)

    @property
    def remapped_count(self) -> int:
        return len(self.remapped)

    @property
    def overridden_count(self) -> int:
        return len(self.overridden)

    @property
    def dropped_count(self) -> int:
        return len(self.dropped)

    @property
    def has_changes(self) -> bool:
        return bool(self.remapped or self.overridden or self.dropped)


def clone_env(
    source: Dict[str, str],
    *,
    key_map: Optional[Dict[str, str]] = None,
    overrides: Optional[Dict[str, str]] = None,
    drop_keys: Optional[List[str]] = None,
) -> CloneResult:
    """Clone *source* into a new dict, applying optional transformations.

    Args:
        source:    The original env mapping to clone.
        key_map:   Rename keys; ``{old_name: new_name}``.  Keys absent from
                   *source* are silently ignored.
        overrides: Force specific values in the cloned env after renaming.
        drop_keys: Keys to exclude from the clone (applied before renaming).

    Returns:
        A :class:`CloneResult` containing the new env and change metadata.
    """
    key_map = key_map or {}
    overrides = overrides or {}
    drop_set = set(drop_keys or [])

    result_env: Dict[str, str] = {}
    remapped: List[str] = []
    dropped: List[str] = []

    for key, value in source.items():
        if key in drop_set:
            dropped.append(key)
            continue

        new_key = key_map.get(key, key)
        if new_key != key:
            remapped.append(key)

        result_env[new_key] = value

    overridden: List[str] = []
    for key, value in overrides.items():
        result_env[key] = value
        overridden.append(key)

    return CloneResult(
        env=result_env,
        remapped=remapped,
        overridden=overridden,
        dropped=dropped,
    )
