"""Tests for envdiff.flatten_reporter."""

from __future__ import annotations

import io

import pytest

from envdiff.flattener import FlattenResult
from envdiff.flatten_reporter import format_flatten_report, print_flatten_report


def _result(**kwargs) -> FlattenResult:
    defaults = {"env": {}, "skipped": [], "separator": "__"}
    defaults.update(kwargs)
    return FlattenResult(**defaults)


class TestFormatFlattenReport:
    def test_header_present(self):
        report = format_flatten_report(_result())
        assert "Flatten Report" in report

    def test_separator_shown(self):
        report = format_flatten_report(_result(separator="_"))
        assert "'_'" in report

    def test_total_keys_shown(self):
        report = format_flatten_report(_result(env={"A": "1", "B": "2"}))
        assert "Total keys: 2" in report

    def test_flattened_keys_listed(self):
        report = format_flatten_report(_result(env={"HOST": "localhost"}))
        assert "HOST" in report
        assert "localhost" in report

    def test_empty_env_shows_no_keys_message(self):
        report = format_flatten_report(_result(env={}))
        assert "no keys produced" in report

    def test_skipped_section_absent_when_none(self):
        report = format_flatten_report(_result(skipped=[]))
        assert "Skipped" not in report

    def test_skipped_section_present(self):
        report = format_flatten_report(_result(skipped=["A__B__C"]))
        assert "Skipped" in report
        assert "A__B__C" in report

    def test_color_flag_does_not_crash(self):
        report = format_flatten_report(_result(env={"X": "y"}), color=True)
        assert "X" in report

    def test_keys_are_sorted_in_output(self):
        report = format_flatten_report(
            _result(env={"Z_KEY": "z", "A_KEY": "a"})
        )
        pos_a = report.index("A_KEY")
        pos_z = report.index("Z_KEY")
        assert pos_a < pos_z


class TestPrintFlattenReport:
    def test_writes_to_provided_file(self):
        buf = io.StringIO()
        print_flatten_report(_result(env={"K": "v"}), color=False, file=buf)
        output = buf.getvalue()
        assert "K" in output

    def test_no_exception_on_empty(self):
        buf = io.StringIO()
        print_flatten_report(_result(), color=False, file=buf)
        assert buf.getvalue() != ""
