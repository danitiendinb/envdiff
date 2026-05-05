"""Tests for envdiff.reporter module."""

import io
import pytest

from envdiff.differ import EnvDiffResult
from envdiff.reporter import format_report, print_report


def _make_result(
    source: dict,
    target: dict,
    missing: set = None,
    extra: set = None,
    differing: set = None,
) -> EnvDiffResult:
    return EnvDiffResult(
        source=source,
        target=target,
        missing_keys=missing or set(),
        extra_keys=extra or set(),
        differing_keys=differing or set(),
    )


class TestFormatReport:
    def test_no_differences(self):
        result = _make_result({"A": "1"}, {"A": "1"})
        report = format_report(result, use_color=False)
        assert report == "No differences found."

    def test_missing_keys_shown(self):
        result = _make_result(
            source={"A": "1", "B": "2"},
            target={"A": "1"},
            missing={"B"},
        )
        report = format_report(result, use_color=False)
        assert "missing from target" in report
        assert "  - B" in report

    def test_extra_keys_shown(self):
        result = _make_result(
            source={"A": "1"},
            target={"A": "1", "C": "3"},
            extra={"C"},
        )
        report = format_report(result, use_color=False)
        assert "not in source" in report
        assert "  + C" in report

    def test_differing_keys_shown(self):
        result = _make_result(
            source={"A": "old"},
            target={"A": "new"},
            differing={"A"},
        )
        report = format_report(result, use_color=False)
        assert "differing values" in report
        assert "  ~ A" in report
        assert "'old'" in report
        assert "'new'" in report

    def test_custom_labels(self):
        result = _make_result(
            source={"X": "1"},
            target={},
            missing={"X"},
        )
        report = format_report(result, source_label="prod", target_label="staging", use_color=False)
        assert "prod" in report
        assert "staging" in report

    def test_color_codes_present_when_enabled(self):
        result = _make_result(
            source={"A": "1"},
            target={},
            missing={"A"},
        )
        report = format_report(result, use_color=True)
        assert "\033[" in report

    def test_color_codes_absent_when_disabled(self):
        result = _make_result(
            source={"A": "1"},
            target={},
            missing={"A"},
        )
        report = format_report(result, use_color=False)
        assert "\033[" not in report

    def test_keys_sorted_in_output(self):
        result = _make_result(
            source={"Z": "1", "A": "2", "M": "3"},
            target={},
            missing={"Z", "A", "M"},
        )
        report = format_report(result, use_color=False)
        idx_a = report.index("  - A")
        idx_m = report.index("  - M")
        idx_z = report.index("  - Z")
        assert idx_a < idx_m < idx_z


class TestPrintReport:
    def test_prints_to_stream(self):
        result = _make_result({"A": "1"}, {"A": "1"})
        buf = io.StringIO()
        print_report(result, use_color=False, file=buf)
        assert "No differences found." in buf.getvalue()
