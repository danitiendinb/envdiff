"""Tests for envdiff.differ3 (side-by-side diff)."""
import pytest
from envdiff.differ3 import SideBySideLine, SideBySideResult, side_by_side_diff


# ---------------------------------------------------------------------------
# SideBySideLine.status
# ---------------------------------------------------------------------------

class TestSideBySideLineStatus:
    def test_same_when_values_equal(self):
        ln = SideBySideLine(key="K", left_value="v", right_value="v")
        assert ln.status == "same"

    def test_changed_when_values_differ(self):
        ln = SideBySideLine(key="K", left_value="a", right_value="b")
        assert ln.status == "changed"

    def test_added_when_left_is_none(self):
        ln = SideBySideLine(key="K", left_value=None, right_value="v")
        assert ln.status == "added"

    def test_removed_when_right_is_none(self):
        ln = SideBySideLine(key="K", left_value="v", right_value=None)
        assert ln.status == "removed"


# ---------------------------------------------------------------------------
# SideBySideResult properties
# ---------------------------------------------------------------------------

def _make_result(lines):
    return SideBySideResult(left_label="A", right_label="B", lines=lines)


class TestSideBySideResult:
    def test_has_changes_false_when_all_same(self):
        r = _make_result([SideBySideLine("K", "v", "v")])
        assert not r.has_changes

    def test_has_changes_true_when_changed(self):
        r = _make_result([SideBySideLine("K", "a", "b")])
        assert r.has_changes

    def test_added_keys(self):
        r = _make_result([
            SideBySideLine("A", None, "1"),
            SideBySideLine("B", "x", "x"),
        ])
        assert r.added_keys == ["A"]

    def test_removed_keys(self):
        r = _make_result([SideBySideLine("X", "v", None)])
        assert r.removed_keys == ["X"]

    def test_changed_keys(self):
        r = _make_result([SideBySideLine("Y", "old", "new")])
        assert r.changed_keys == ["Y"]


# ---------------------------------------------------------------------------
# side_by_side_diff
# ---------------------------------------------------------------------------

class TestSideBySideDiff:
    def test_empty_envs_produce_no_lines(self):
        r = side_by_side_diff({}, {})
        assert r.lines == []

    def test_keys_are_sorted(self):
        r = side_by_side_diff({"B": "2", "A": "1"}, {})
        assert [ln.key for ln in r.lines] == ["A", "B"]

    def test_common_key_same_value(self):
        r = side_by_side_diff({"K": "v"}, {"K": "v"})
        assert r.lines[0].status == "same"

    def test_common_key_different_value(self):
        r = side_by_side_diff({"K": "old"}, {"K": "new"})
        assert r.lines[0].status == "changed"
        assert r.lines[0].left_value == "old"
        assert r.lines[0].right_value == "new"

    def test_left_only_key_is_removed(self):
        r = side_by_side_diff({"GONE": "v"}, {})
        assert r.lines[0].status == "removed"
        assert r.lines[0].right_value is None

    def test_right_only_key_is_added(self):
        r = side_by_side_diff({}, {"NEW": "v"})
        assert r.lines[0].status == "added"
        assert r.lines[0].left_value is None

    def test_labels_stored_on_result(self):
        r = side_by_side_diff({}, {}, left_label="base", right_label="prod")
        assert r.left_label == "base"
        assert r.right_label == "prod"

    def test_default_labels(self):
        r = side_by_side_diff({}, {})
        assert r.left_label == "left"
        assert r.right_label == "right"
