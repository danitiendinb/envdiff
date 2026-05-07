"""Tests for envdiff.profile_reporter."""

import pytest
from envdiff.profiler import profile_env
from envdiff.profile_reporter import format_profile_report


def _report(env, color=False):
    return format_profile_report(profile_env(env), color=color)


class TestFormatProfileReport:
    def test_total_keys_shown(self):
        report = _report({"A": "1", "B": "2"})
        assert "Total keys" in report
        assert "2" in report

    def test_empty_values_section_present(self):
        report = _report({"A": ""})
        assert "Empty Values" in report
        assert "A" in report

    def test_no_empty_values_shows_none(self):
        report = _report({"A": "val"})
        assert "(none)" in report

    def test_sensitive_keys_shown(self):
        report = _report({"DB_PASSWORD": "x"})
        assert "Sensitive Keys" in report
        assert "DB_PASSWORD" in report

    def test_duplicate_values_shown(self):
        report = _report({"A": "dup", "B": "dup"})
        assert "Duplicate Values" in report
        assert "dup" in report

    def test_color_adds_escape_codes(self):
        report = _report({"DB_TOKEN": ""}, color=True)
        assert "\033[" in report

    def test_no_color_no_escape_codes(self):
        report = _report({"DB_TOKEN": ""}, color=False)
        assert "\033[" not in report

    def test_empty_env_renders_cleanly(self):
        report = _report({})
        assert "Total keys" in report
        assert "0" in report

    def test_long_value_truncated_in_duplicate_section(self):
        long_val = "x" * 50
        report = _report({"A": long_val, "B": long_val})
        assert "..." in report
