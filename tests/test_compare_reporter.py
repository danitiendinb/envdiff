"""Tests for envdiff.compare_reporter."""

import pytest
from datetime import datetime
from envdiff.comparator import compare_snapshots
from envdiff.compare_reporter import format_compare_report
from envdiff.snapshotter import Snapshot


def _snap(label: str, env: dict) -> Snapshot:
    return Snapshot(label=label, timestamp=datetime(2024, 1, 1), env=env)


def _result(source_env: dict, target_env: dict):
    return compare_snapshots(_snap("src", source_env), _snap("tgt", target_env))


class TestFormatCompareReport:
    def test_header_contains_labels(self):
        report = format_compare_report(_result({}, {}))
        assert "src" in report
        assert "tgt" in report

    def test_no_changes_message(self):
        report = format_compare_report(_result({"K": "v"}, {"K": "v"}))
        assert "No changes detected" in report

    def test_added_key_shown(self):
        report = format_compare_report(_result({}, {"NEW_KEY": "hello"}))
        assert "NEW_KEY" in report
        assert "hello" in report
        assert "+" in report

    def test_removed_key_shown(self):
        report = format_compare_report(_result({"OLD": "bye"}, {}))
        assert "OLD" in report
        assert "-" in report

    def test_modified_key_shown(self):
        report = format_compare_report(_result({"X": "a"}, {"X": "b"}))
        assert "X" in report
        assert "~" in report
        assert "'a'" in report
        assert "'b'" in report

    def test_section_counts_shown(self):
        report = format_compare_report(_result({}, {"A": "1", "B": "2"}))
        assert "Added (2)" in report

    def test_no_color_by_default(self):
        report = format_compare_report(_result({}, {"K": "v"}))
        assert "\033[" not in report

    def test_color_codes_present_when_enabled(self):
        report = format_compare_report(_result({}, {"K": "v"}), use_color=True)
        assert "\033[" in report
