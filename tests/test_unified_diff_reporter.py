"""Tests for envdiff.unified_diff_reporter."""
from __future__ import annotations

from envdiff.differ2 import unified_diff
from envdiff.unified_diff_reporter import format_unified_diff_report


def _fmt(a: dict, b: dict, context: bool = True, use_color: bool = False) -> str:
    result = unified_diff(a, b, label_a="a.env", label_b="b.env", context=context)
    return format_unified_diff_report(result, use_color=use_color)


class TestFormatUnifiedDiffReport:
    def test_header_contains_labels(self):
        out = _fmt({}, {})
        assert "--- a.env" in out
        assert "+++ b.env" in out

    def test_no_differences_message(self):
        out = _fmt({"A": "1"}, {"A": "1"})
        assert "no differences" in out

    def test_added_key_shown_with_plus(self):
        out = _fmt({}, {"NEW": "val"})
        assert "+ NEW=val" in out

    def test_removed_key_shown_with_minus(self):
        out = _fmt({"OLD": "val"}, {})
        assert "- OLD=val" in out

    def test_changed_key_shows_both_lines(self):
        out = _fmt({"K": "before"}, {"K": "after"})
        assert "- K=before" in out
        assert "+ K=after" in out

    def test_context_line_shown_with_indent(self):
        out = _fmt({"SAME": "v"}, {"SAME": "v"}, context=True)
        assert "  SAME=v" in out

    def test_summary_added_count(self):
        out = _fmt({}, {"A": "1", "B": "2"})
        assert "+2 added" in out

    def test_summary_removed_count(self):
        out = _fmt({"X": "1"}, {})
        assert "-1 removed" in out

    def test_summary_changed_count(self):
        out = _fmt({"K": "old"}, {"K": "new"})
        assert "~1 changed" in out

    def test_no_color_produces_plain_text(self):
        out = _fmt({}, {"K": "v"}, use_color=False)
        assert "\033[" not in out
