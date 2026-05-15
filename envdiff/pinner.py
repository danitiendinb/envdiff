"""Pin environment variable values to a snapshot for drift detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinEntry:
    key: str
    pinned_value: str
    current_value: Optional[str]

    @property
    def is_drifted(self) -> bool:
        return self.current_value != self.pinned_value

    @property
    def is_missing(self) -> bool:
        return self.current_value is None


@dataclass
class PinResult:
    entries: List[PinEntry] = field(default_factory=list)

    @property
    def drifted(self) -> List[PinEntry]:
        return [e for e in self.entries if e.is_drifted and not e.is_missing]

    @property
    def missing(self) -> List[PinEntry]:
        return [e for e in self.entries if e.is_missing]

    @property
    def stable(self) -> List[PinEntry]:
        return [e for e in self.entries if not e.is_drifted]

    @property
    def has_drift(self) -> bool:
        return bool(self.drifted or self.missing)

    def drift_count(self) -> int:
        return len(self.drifted) + len(self.missing)


def pin_env(
    pinned: Dict[str, str],
    current: Dict[str, str],
    keys: Optional[List[str]] = None,
) -> PinResult:
    """Compare pinned values against the current env.

    Args:
        pinned: The reference (pinned) env mapping.
        current: The live env mapping to check against.
        keys: Optional subset of keys to evaluate. Defaults to all pinned keys.

    Returns:
        A PinResult describing stable, drifted, and missing keys.
    """
    check_keys = keys if keys is not None else list(pinned.keys())
    entries: List[PinEntry] = []

    for key in sorted(check_keys):
        pinned_value = pinned.get(key, "")
        current_value = current.get(key)  # None if absent
        entries.append(PinEntry(key=key, pinned_value=pinned_value, current_value=current_value))

    return PinResult(entries=entries)
