"""Key-value comparator that produces a unified diff between two env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffLine:
    """A single line in a unified diff output."""

    kind: str  # 'context', 'added', 'removed', 'changed'
    key: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    @property
    def symbol(self) -> str:
        return {
            "context": " ",
            "added": "+",
            "removed": "-",
            "changed": "~",
        }.get(self.kind, "?")


@dataclass
class UnifiedDiffResult:
    """Result of a unified diff between two env mappings."""

    lines: List[DiffLine] = field(default_factory=list)
    label_a: str = "a"
    label_b: str = "b"

    @property
    def has_changes(self) -> bool:
        return any(ln.kind != "context" for ln in self.lines)

    @property
    def added_keys(self) -> List[str]:
        return [ln.key for ln in self.lines if ln.kind == "added"]

    @property
    def removed_keys(self) -> List[str]:
        return [ln.key for ln in self.lines if ln.kind == "removed"]

    @property
    def changed_keys(self) -> List[str]:
        return [ln.key for ln in self.lines if ln.kind == "changed"]


def unified_diff(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    label_a: str = "a",
    label_b: str = "b",
    context: bool = True,
) -> UnifiedDiffResult:
    """Produce a unified diff between *env_a* and *env_b*.

    Keys are compared in sorted order.  When *context* is True, keys that
    are identical in both envs are included as context lines.
    """
    all_keys = sorted(set(env_a) | set(env_b))
    lines: List[DiffLine] = []

    for key in all_keys:
        in_a = key in env_a
        in_b = key in env_b

        if in_a and in_b:
            if env_a[key] == env_b[key]:
                if context:
                    lines.append(DiffLine(kind="context", key=key, old_value=env_a[key], new_value=env_b[key]))
            else:
                lines.append(DiffLine(kind="changed", key=key, old_value=env_a[key], new_value=env_b[key]))
        elif in_a:
            lines.append(DiffLine(kind="removed", key=key, old_value=env_a[key]))
        else:
            lines.append(DiffLine(kind="added", key=key, new_value=env_b[key]))

    return UnifiedDiffResult(lines=lines, label_a=label_a, label_b=label_b)
