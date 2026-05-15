"""Tests for envdiff.side_by_side_reporter."""
from envdiff.differ3 import side_by_side_diff
from envdiff.side_by_side_reporter import format_side_by_side_report


def _fmt(left, right, **kw):
    result = side_by_side_diff(left, right, left_label="L", right_label="R")
    return format_side_by_side_report(result, use_color=False, **kw)


class TestFormatSideBySideReport:
    def test_header_contains_labels(self):
        out = _fmt({}, {})
        assert "L" in out
        assert "R" in out

    def test_no_keys_message(self):
        out = _fmt({}, {})
        assert "no keys" in out

    def test_same_key_shown_with_space_symbol(self):
        out = _fmt({"FOO": "bar"}, {"FOO": "bar"})
        assert "FOO" in out
        # space prefix for same lines
        for line in out.splitlines():
            if "FOO" in line:
                assert line.startswith(" ")

    def test_added_key_shown_with_plus(self):
        out = _fmt({}, {"NEW": "1"})
        for line in out.splitlines():
            if "NEW" in line:
                assert line.startswith("+")

    def test_removed_key_shown_with_minus(self):
        out = _fmt({"OLD": "v"}, {})
        for line in out.splitlines():
            if "OLD" in line:
                assert line.startswith("-")

    def test_changed_key_shown_with_tilde(self):
        out = _fmt({"K": "old"}, {"K": "new"})
        for line in out.splitlines():
            if "K" in line and "old" in line:
                assert line.startswith("~")

    def test_summary_line_present(self):
        out = _fmt({"A": "1"}, {"A": "2", "B": "3"})
        assert "Summary:" in out

    def test_summary_counts_correct(self):
        out = _fmt({"A": "1", "B": "old"}, {"B": "new", "C": "3"})
        # A removed, B changed, C added
        assert "1 changed" in out
        assert "1 added" in out
        assert "1 removed" in out

    def test_col_width_respected(self):
        out = _fmt({"K": "v"}, {"K": "v"}, col_width=10)
        # value column should be padded to 10 chars
        for line in out.splitlines():
            if line.startswith(" K"):
                parts = line.split("  ")
                assert len(parts) >= 3
