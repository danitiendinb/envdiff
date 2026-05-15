"""Split a single env dict into multiple partitions based on rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    partitions: Dict[str, Dict[str, str]]
    unmatched: Dict[str, str]

    def partition_names(self) -> List[str]:
        return list(self.partitions.keys())

    def has_unmatched(self) -> bool:
        return bool(self.unmatched)

    def total_keys(self) -> int:
        total = sum(len(v) for v in self.partitions.values())
        return total + len(self.unmatched)


def split_by_prefix(
    env: Dict[str, str],
    prefixes: List[str],
    *,
    delimiter: str = "_",
    strip_prefix: bool = False,
) -> SplitResult:
    """Partition *env* into buckets keyed by prefix.

    Keys that match no prefix land in ``unmatched``.
    When *strip_prefix* is True the prefix (and delimiter) are removed
    from the key in the output partition.
    """
    partitions: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    unmatched: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            candidate = prefix + delimiter
            if key.upper().startswith(candidate.upper()):
                out_key = key[len(candidate):] if strip_prefix else key
                partitions[prefix][out_key] = value
                matched = True
                break
        if not matched:
            unmatched[key] = value

    return SplitResult(partitions=partitions, unmatched=unmatched)


def split_by_keys(
    env: Dict[str, str],
    groups: Dict[str, List[str]],
) -> SplitResult:
    """Partition *env* by explicit key lists supplied in *groups*.

    Keys not listed in any group land in ``unmatched``.
    """
    partitions: Dict[str, Dict[str, str]] = {name: {} for name in groups}
    assigned: set = set()

    for group_name, keys in groups.items():
        for key in keys:
            if key in env:
                partitions[group_name][key] = env[key]
                assigned.add(key)

    unmatched = {k: v for k, v in env.items() if k not in assigned}
    return SplitResult(partitions=partitions, unmatched=unmatched)
