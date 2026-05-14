"""Group environment variables by prefix or custom rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]]
    ungrouped: Dict[str, str]

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def all_keys(self) -> List[str]:
        keys: List[str] = []
        for env in self.groups.values():
            keys.extend(env.keys())
        keys.extend(self.ungrouped.keys())
        return sorted(keys)

    def total_groups(self) -> int:
        return len(self.groups)


def _extract_prefix(key: str, delimiter: str = "_") -> Optional[str]:
    """Return the first segment before the delimiter, or None if absent."""
    if delimiter in key:
        return key.split(delimiter, 1)[0]
    return None


def group_by_prefix(
    env: Dict[str, str],
    delimiter: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Group keys by their prefix segment.

    Keys whose prefix group has fewer than *min_group_size* members are
    placed in *ungrouped*.
    """
    buckets: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        prefix = _extract_prefix(key, delimiter)
        if prefix:
            buckets.setdefault(prefix, {})[key] = value
        else:
            buckets.setdefault("", {})[key] = value

    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}

    for prefix, members in buckets.items():
        if prefix == "" or len(members) < min_group_size:
            ungrouped.update(members)
        else:
            groups[prefix] = members

    return GroupResult(groups=groups, ungrouped=ungrouped)


def group_by_rules(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
) -> GroupResult:
    """Group keys according to explicit *rules* mapping group name -> key list.

    Keys not mentioned in any rule end up in *ungrouped*.
    """
    assigned: set[str] = set()
    groups: Dict[str, Dict[str, str]] = {}

    for group_name, keys in rules.items():
        members: Dict[str, str] = {}
        for key in keys:
            if key in env:
                members[key] = env[key]
                assigned.add(key)
        if members:
            groups[group_name] = members

    ungrouped = {k: v for k, v in env.items() if k not in assigned}
    return GroupResult(groups=groups, ungrouped=ungrouped)
