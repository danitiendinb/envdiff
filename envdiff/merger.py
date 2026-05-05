"""Merge multiple .env mappings into a single resolved mapping.

Later sources take precedence over earlier ones (last-write-wins),
with optional conflict tracking so callers can inspect overwritten keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class MergeResult:
    """Outcome of merging two or more env mappings."""

    merged: Dict[str, str]
    # key -> list of (source_index, value) pairs that were overwritten
    conflicts: Dict[str, List[Tuple[int, str]]] = field(default_factory=dict)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)


def merge_envs(
    *envs: Dict[str, str],
    track_conflicts: bool = True,
) -> MergeResult:
    """Merge *envs* left-to-right; later mappings override earlier ones.

    Parameters
    ----------
    *envs:
        Two or more ``{key: value}`` dictionaries to merge.
    track_conflicts:
        When *True* (default), record every key whose value was overwritten
        so callers can surface warnings or audit logs.

    Returns
    -------
    MergeResult
        The merged mapping and any conflict details.
    """
    if not envs:
        return MergeResult(merged={})

    merged: Dict[str, str] = {}
    conflicts: Dict[str, List[Tuple[int, str]]] = {}

    for source_index, env in enumerate(envs):
        for key, value in env.items():
            if track_conflicts and key in merged:
                conflicts.setdefault(key, [])
                # Record the source that is being overwritten and its value
                previous_source = source_index - 1
                # Walk back to find the actual last source that set this key
                for prev_idx in range(source_index - 1, -1, -1):
                    if key in envs[prev_idx]:  # type: ignore[index]
                        previous_source = prev_idx
                        break
                conflicts[key].append((previous_source, merged[key]))
            merged[key] = value

    return MergeResult(merged=merged, conflicts=conflicts)


def merge_env_files(
    *paths: str,
    track_conflicts: bool = True,
) -> MergeResult:
    """Convenience wrapper that parses files from disk before merging."""
    from envdiff.parser import parse_env_file

    envs = [parse_env_file(p) for p in paths]
    return merge_envs(*envs, track_conflicts=track_conflicts)
