"""Side-by-side diff of two env dicts, producing aligned column output."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SideBySideLine:
    key: str
    left_value: Optional[str]   # None => key absent on left
    right_value: Optional[str]  # None => key absent on right

    @property
    def status(self) -> str:
        if self.left_value is None:
            return "added"
        if self.right_value is None:
            return "removed"
        if self.left_value != self.right_value:
            return "changed"
        return "same"


@dataclass
class SideBySideResult:
    left_label: str
    right_label: str
    lines: List[SideBySideLine] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(ln.status != "same" for ln in self.lines)

    @property
    def added_keys(self) -> List[str]:
        return [ln.key for ln in self.lines if ln.status == "added"]

    @property
    def removed_keys(self) -> List[str]:
        return [ln.key for ln in self.lines if ln.status == "removed"]

    @property
    def changed_keys(self) -> List[str]:
        return [ln.key for ln in self.lines if ln.status == "changed"]


def side_by_side_diff(
    left: Dict[str, str],
    right: Dict[str, str],
    left_label: str = "left",
    right_label: str = "right",
) -> SideBySideResult:
    """Produce a sorted, aligned side-by-side diff of two env dicts."""
    all_keys = sorted(set(left) | set(right))
    lines = [
        SideBySideLine(
            key=k,
            left_value=left.get(k),
            right_value=right.get(k),
        )
        for k in all_keys
    ]
    return SideBySideResult(left_label=left_label, right_label=right_label, lines=lines)
