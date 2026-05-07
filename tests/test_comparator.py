"""Tests for envdiff.comparator."""

import pytest
from envdiff.comparator import compare_snapshots, CompareResult, EnvChange
from envdiff.snapshotter import Snapshot
from datetime import datetime


def _snap(label: str, env: dict) -> Snapshot:
    return Snapshot(label=label, timestamp=datetime(2024, 1, 1), env=env)


class TestCompareSnapshots:
    def test_no_changes_when_identical(self):
        s = _snap("a", {"KEY": "val"})
        t = _snap("b", {"KEY": "val"})
        result = compare_snapshots(s, t)
        assert not result.has_changes

    def test_added_key_detected(self):
        s = _snap("a", {})
        t = _snap("b", {"NEW": "1"})
        result = compare_snapshots(s, t)
        assert len(result.added) == 1
        assert result.added[0].key == "NEW"
        assert result.added[0].new_value == "1"

    def test_removed_key_detected(self):
        s = _snap("a", {"OLD": "x"})
        t = _snap("b", {})
        result = compare_snapshots(s, t)
        assert len(result.removed) == 1
        assert result.removed[0].key == "OLD"
        assert result.removed[0].old_value == "x"

    def test_modified_key_detected(self):
        s = _snap("a", {"K": "old"})
        t = _snap("b", {"K": "new"})
        result = compare_snapshots(s, t)
        assert len(result.modified) == 1
        c = result.modified[0]
        assert c.key == "K"
        assert c.old_value == "old"
        assert c.new_value == "new"

    def test_labels_preserved_in_result(self):
        s = _snap("staging", {})
        t = _snap("production", {})
        result = compare_snapshots(s, t)
        assert result.source_label == "staging"
        assert result.target_label == "production"

    def test_mixed_changes(self):
        s = _snap("a", {"A": "1", "B": "2", "C": "3"})
        t = _snap("b", {"A": "1", "B": "99", "D": "4"})
        result = compare_snapshots(s, t)
        assert len(result.added) == 1
        assert result.added[0].key == "D"
        assert len(result.removed) == 1
        assert result.removed[0].key == "C"
        assert len(result.modified) == 1
        assert result.modified[0].key == "B"

    def test_empty_both_no_changes(self):
        result = compare_snapshots(_snap("a", {}), _snap("b", {}))
        assert not result.has_changes
        assert result.changes == []

    def test_changes_sorted_by_key(self):
        s = _snap("a", {"Z": "1", "A": "1"})
        t = _snap("b", {"Z": "2", "A": "2"})
        result = compare_snapshots(s, t)
        keys = [c.key for c in result.changes]
        assert keys == sorted(keys)
