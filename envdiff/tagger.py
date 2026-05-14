"""Tag env keys with user-defined labels for grouping and annotation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set


@dataclass
class TagResult:
    """Result of tagging an env dict."""

    env: Dict[str, str]
    tags: Dict[str, FrozenSet[str]]  # key -> set of tag labels
    tag_index: Dict[str, List[str]]  # tag label -> list of keys

    def keys_for_tag(self, tag: str) -> List[str]:
        """Return all keys that carry *tag*."""
        return self.tag_index.get(tag, [])

    def tags_for_key(self, key: str) -> FrozenSet[str]:
        """Return all tags assigned to *key*."""
        return self.tags.get(key, frozenset())

    def all_tags(self) -> List[str]:
        """Sorted list of every tag present in the result."""
        return sorted(self.tag_index.keys())


def tag_env(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
) -> TagResult:
    """Apply *rules* to *env* and return a :class:`TagResult`.

    Parameters
    ----------
    env:
        Parsed environment dictionary.
    rules:
        Mapping of ``tag_label -> list_of_key_substrings``.  A key is tagged
        with a label when its name contains **any** of the listed substrings
        (case-insensitive).
    """
    tags: Dict[str, Set[str]] = {k: set() for k in env}
    tag_index: Dict[str, List[str]] = {}

    for label, patterns in rules.items():
        matched: List[str] = []
        for key in env:
            for pattern in patterns:
                if pattern.lower() in key.lower():
                    tags[key].add(label)
                    matched.append(key)
                    break
        tag_index[label] = sorted(matched)

    frozen_tags: Dict[str, FrozenSet[str]] = {
        k: frozenset(v) for k, v in tags.items()
    }
    return TagResult(env=env, tags=frozen_tags, tag_index=tag_index)
