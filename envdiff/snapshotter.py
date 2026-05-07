"""Snapshotter: capture and compare env file snapshots over time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from envdiff.parser import parse_env_file


@dataclass
class Snapshot:
    """A point-in-time capture of an env file's contents."""

    path: str
    captured_at: str
    env: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "captured_at": self.captured_at,
            "env": self.env,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            path=data["path"],
            captured_at=data["captured_at"],
            env=data.get("env", {}),
        )


def capture_snapshot(env_path: str) -> Snapshot:
    """Read an env file and return a Snapshot of its current state."""
    env = parse_env_file(env_path)
    captured_at = datetime.now(timezone.utc).isoformat()
    return Snapshot(path=env_path, captured_at=captured_at, env=env)


def save_snapshot(snapshot: Snapshot, snapshot_path: str) -> None:
    """Persist a Snapshot to a JSON file."""
    with open(snapshot_path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(snapshot_path: str) -> Snapshot:
    """Load a previously saved Snapshot from a JSON file."""
    with open(snapshot_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)


def diff_snapshots(
    old: Snapshot, new: Snapshot
) -> Dict[str, dict]:
    """Return a structured diff between two snapshots.

    Returns a dict with keys 'added', 'removed', 'changed', each mapping
    key names to relevant values.
    """
    old_env = old.env
    new_env = new.env

    added = {k: new_env[k] for k in new_env if k not in old_env}
    removed = {k: old_env[k] for k in old_env if k not in new_env}
    changed = {
        k: {"old": old_env[k], "new": new_env[k]}
        for k in old_env
        if k in new_env and old_env[k] != new_env[k]
    }

    return {"added": added, "removed": removed, "changed": changed}
