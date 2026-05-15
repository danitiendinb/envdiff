"""Tests for envdiff.differ2 (unified diff logic)."""
from __future__ import annotations

import pytest

from envdiff.differ2 import DiffLine, UnifiedDiffResult, unified_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _diff(a: dict, b: dict, context: bool = True) -> UnifiedDiffResult:
    return unified_diff(a, b, label_a="a.env", label_b="b.env", context=context)


# ---------------------------------------------------------------------------
# UnifiedDiffResult properties
# ---------------------------------------------------------------------------

class TestUnifiedDiffResult:
    def test_has_changes_false_when_only_context(self):
        result = _diff({"A": "1"}, {"A": "1"})
        assert not result.has_changes

    def test_has_changes_true_when_added(self):
        result = _diff({}, {"A": "1"})
        assert result.has_changes

    def test_added_keys_populated(self):
        result = _diff({}, {"X": "v", "Y": "w"})
        assert sorted(result.added_keys) == ["X", "Y"]

    def test_removed_keys_populated(self):
        result = _diff({"OLD": "1"}, {})
        assert result.removed_keys == ["OLD"]

    def test_changed_keys_populated(self):
        result = _diff({"K": "old"}, {"K": "new"})
        assert result.changed_keys == ["K"]

    def test_labels_stored(self):
        result = unified_diff({}, {}, label_a="x", label_b="y")
        assert result.label_a == "x"
        assert result.label_b == "y"


# ---------------------------------------------------------------------------
# unified_diff behaviour
# ---------------------------------------------------------------------------

class TestUnifiedDiff:
    def test_identical_envs_produce_only_context_lines(self):
        env = {"A": "1", "B": "2"}
        result = _diff(env, env)
        assert all(ln.kind == "context" for ln in result.lines)

    def test_no_context_omits_unchanged_keys(self):
        env_a = {"A": "1", "B": "2"}
        env_b = {"A": "1", "B": "changed"}
        result = _diff(env_a, env_b, context=False)
        assert all(ln.key != "A" for ln in result.lines)
        assert any(ln.key == "B" for ln in result.lines)

    def test_added_line_has_new_value(self):
        result = _diff({}, {"NEW": "hello"})
        line = result.lines[0]
        assert line.kind == "added"
        assert line.new_value == "hello"
        assert line.old_value is None

    def test_removed_line_has_old_value(self):
        result = _diff({"GONE": "bye"}, {})
        line = result.lines[0]
        assert line.kind == "removed"
        assert line.old_value == "bye"
        assert line.new_value is None

    def test_changed_line_has_both_values(self):
        result = _diff({"K": "before"}, {"K": "after"})
        line = result.lines[0]
        assert line.kind == "changed"
        assert line.old_value == "before"
        assert line.new_value == "after"

    def test_keys_are_sorted(self):
        result = _diff({"Z": "1", "A": "2"}, {"Z": "1", "A": "2"})
        keys = [ln.key for ln in result.lines]
        assert keys == sorted(keys)

    def test_symbol_property(self):
        assert DiffLine(kind="added", key="K", new_value="v").symbol == "+"
        assert DiffLine(kind="removed", key="K", old_value="v").symbol == "-"
        assert DiffLine(kind="changed", key="K", old_value="a", new_value="b").symbol == "~"
        assert DiffLine(kind="context", key="K", old_value="v", new_value="v").symbol == " "
