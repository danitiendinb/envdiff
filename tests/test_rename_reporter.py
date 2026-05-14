"""Tests for envdiff.rename_reporter."""

import io
from envdiff.renamer import RenameResult
from envdiff.rename_reporter import format_rename_report, print_rename_report


def _result(
    env=None,
    renamed=None,
    skipped=None,
    overwritten=None,
):
    return RenameResult(
        env=env or {},
        renamed=renamed or [],
        skipped=skipped or [],
        overwritten=overwritten or [],
    )


class TestFormatRenameReport:
    def test_header_present(self):
        report = format_rename_report(_result(), color=False)
        assert "Rename Report" in report

    def test_no_renames_shows_message(self):
        report = format_rename_report(_result(), color=False)
        assert "No keys were renamed" in report

    def test_renamed_keys_listed(self):
        result = _result(renamed=[("OLD", "NEW")])
        report = format_rename_report(result, color=False)
        assert "OLD" in report
        assert "NEW" in report
        assert "->" in report

    def test_skipped_keys_listed(self):
        result = _result(skipped=["GHOST"])
        report = format_rename_report(result, color=False)
        assert "GHOST" in report
        assert "Skipped" in report

    def test_overwritten_keys_listed(self):
        result = _result(overwritten=["CONFLICT"])
        report = format_rename_report(result, color=False)
        assert "CONFLICT" in report
        assert "Overwritten" in report

    def test_color_codes_present_when_enabled(self):
        result = _result(renamed=[("A", "B")])
        report = format_rename_report(result, color=True)
        assert "\033[" in report

    def test_no_color_codes_when_disabled(self):
        result = _result(renamed=[("A", "B")])
        report = format_rename_report(result, color=False)
        assert "\033[" not in report

    def test_rename_count_shown(self):
        result = _result(renamed=[("A", "B"), ("C", "D")])
        report = format_rename_report(result, color=False)
        assert "2" in report


class TestPrintRenameReport:
    def test_print_writes_to_file(self):
        buf = io.StringIO()
        result = _result(renamed=[("OLD", "NEW")])
        print_rename_report(result, color=False, file=buf)
        output = buf.getvalue()
        assert "OLD" in output
        assert "NEW" in output
