"""Diff logic for comparing two parsed .env dictionaries."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvDiffResult:
    """Holds the result of diffing two .env environments."""

    added: Dict[str, str] = field(default_factory=dict)
    """Keys present in *right* but not in *left*."""

    removed: Dict[str, str] = field(default_factory=dict)
    """Keys present in *left* but not in *right*."""

    changed: Dict[str, tuple] = field(default_factory=dict)
    """Keys present in both but with different values: {key: (left_val, right_val)}."""

    unchanged: List[str] = field(default_factory=list)
    """Keys present in both with identical values."""

    @property
    def has_differences(self) -> bool:
        """Return True if any differences exist between the two envs."""
        return bool(self.added or self.removed or self.changed)


def diff_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    left_label: str = "left",
    right_label: str = "right",
) -> EnvDiffResult:
    """Compare two .env dictionaries and return a structured diff.

    Args:
        left:  Base environment (e.g. production).
        right: Target environment (e.g. staging).
        left_label:  Human-readable label for *left* (used in repr).
        right_label: Human-readable label for *right* (used in repr).

    Returns:
        An :class:`EnvDiffResult` describing all differences.
    """
    result = EnvDiffResult()
    all_keys = set(left) | set(right)

    for key in sorted(all_keys):
        in_left = key in left
        in_right = key in right

        if in_left and not in_right:
            result.removed[key] = left[key]
        elif in_right and not in_left:
            result.added[key] = right[key]
        elif left[key] != right[key]:
            result.changed[key] = (left[key], right[key])
        else:
            result.unchanged.append(key)

    return result
