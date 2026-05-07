"""Tests for envdiff.snapshotter."""

import json
import os
import tempfile

import pytest

from envdiff.snapshotter import (
    Snapshot,
    capture_snapshot,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
)


def _write_env(tmp_path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# Snapshot dataclass
# ---------------------------------------------------------------------------

class TestSnapshotRoundtrip:
    def test_to_dict_contains_all_fields(self):
        s = Snapshot(path=".env", captured_at="2024-01-01T00:00:00+00:00", env={"A": "1"})
        d = s.to_dict()
        assert d["path"] == ".env"
        assert d["captured_at"] == "2024-01-01T00:00:00+00:00"
        assert d["env"] == {"A": "1"}

    def test_from_dict_reconstructs_snapshot(self):
        data = {"path": ".env", "captured_at": "2024-01-01T00:00:00+00:00", "env": {"X": "y"}}
        s = Snapshot.from_dict(data)
        assert s.path == ".env"
        assert s.env == {"X": "y"}

    def test_from_dict_missing_env_defaults_empty(self):
        data = {"path": ".env", "captured_at": "ts"}
        s = Snapshot.from_dict(data)
        assert s.env == {}


# ---------------------------------------------------------------------------
# capture_snapshot
# ---------------------------------------------------------------------------

def test_capture_snapshot_reads_env_file(tmp_path):
    env_file = _write_env(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    snap = capture_snapshot(env_file)
    assert snap.env == {"FOO": "bar", "BAZ": "qux"}
    assert snap.path == env_file
    assert snap.captured_at  # non-empty timestamp


# ---------------------------------------------------------------------------
# save_snapshot / load_snapshot
# ---------------------------------------------------------------------------

def test_save_and_load_snapshot_roundtrip(tmp_path):
    env_file = _write_env(tmp_path, ".env", "KEY=value\n")
    snap = capture_snapshot(env_file)
    snap_file = str(tmp_path / "snap.json")
    save_snapshot(snap, snap_file)

    loaded = load_snapshot(snap_file)
    assert loaded.path == snap.path
    assert loaded.env == snap.env
    assert loaded.captured_at == snap.captured_at


def test_save_snapshot_produces_valid_json(tmp_path):
    snap = Snapshot(path=".env", captured_at="ts", env={"A": "1"})
    snap_file = str(tmp_path / "snap.json")
    save_snapshot(snap, snap_file)
    with open(snap_file) as fh:
        data = json.load(fh)
    assert data["env"]["A"] == "1"


# ---------------------------------------------------------------------------
# diff_snapshots
# ---------------------------------------------------------------------------

class TestDiffSnapshots:
    def _snap(self, env: dict) -> Snapshot:
        return Snapshot(path=".env", captured_at="ts", env=env)

    def test_added_keys_detected(self):
        old = self._snap({"A": "1"})
        new = self._snap({"A": "1", "B": "2"})
        result = diff_snapshots(old, new)
        assert result["added"] == {"B": "2"}
        assert result["removed"] == {}
        assert result["changed"] == {}

    def test_removed_keys_detected(self):
        old = self._snap({"A": "1", "B": "2"})
        new = self._snap({"A": "1"})
        result = diff_snapshots(old, new)
        assert result["removed"] == {"B": "2"}
        assert result["added"] == {}

    def test_changed_keys_detected(self):
        old = self._snap({"A": "old"})
        new = self._snap({"A": "new"})
        result = diff_snapshots(old, new)
        assert result["changed"] == {"A": {"old": "old", "new": "new"}}

    def test_no_differences_all_empty(self):
        snap = self._snap({"A": "1", "B": "2"})
        result = diff_snapshots(snap, snap)
        assert result == {"added": {}, "removed": {}, "changed": {}}
