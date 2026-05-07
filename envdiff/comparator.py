"""Compare two env snapshots and produce a structured change report."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.snapshotter import Snapshot


@dataclass
class EnvChange:
    key: str
    change_type: str  # 'added', 'removed', 'modified'
    old_value: str | None = None
    new_value: str | None = None


@dataclass
class CompareResult:
    source_label: str
    target_label: str
    changes: List[EnvChange] = field(default_factory=list)

    @property
    def added(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == "added"]

    @property
    def removed(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == "removed"]

    @property
    def modified(self) -> List[EnvChange]:
        return [c for c in self.changes if c.change_type == "modified"]

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)


def compare_snapshots(source: Snapshot, target: Snapshot) -> CompareResult:
    """Return a CompareResult describing what changed between two snapshots."""
    result = CompareResult(
        source_label=source.label,
        target_label=target.label,
    )

    source_env: Dict[str, str] = source.env
    target_env: Dict[str, str] = target.env

    all_keys = sorted(set(source_env) | set(target_env))

    for key in all_keys:
        in_source = key in source_env
        in_target = key in target_env

        if in_source and not in_target:
            result.changes.append(EnvChange(key=key, change_type="removed", old_value=source_env[key]))
        elif in_target and not in_source:
            result.changes.append(EnvChange(key=key, change_type="added", new_value=target_env[key]))
        elif source_env[key] != target_env[key]:
            result.changes.append(
                EnvChange(
                    key=key,
                    change_type="modified",
                    old_value=source_env[key],
                    new_value=target_env[key],
                )
            )

    return result
