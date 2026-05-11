"""Tests for envdiff.transform_reporter."""

from __future__ import annotations

import io

import pytest

from envdiff.transformer import transform_env
from envdiff.transform_reporter import format_transform_report, print_transform_report


def _result(env: dict, **kwargs):
    return transform_env(env, **kwargs)


class TestFormatTransformReport:
    def test_header_present(self):
        r = _result({"A": "1"})
        report = format_transform_report(r, color=False)
        assert "Transform Report" in report

    def test_no_changes_message_when_unchanged(self):
        r = _result({"A": "1"})
        report = format_transform_report(r, color=False)
        assert "No values changed" in report

    def test_applied_transformations_listed(self):
        r = _result({"foo": "bar"}, uppercase_keys=True, strip_whitespace=True)
        report = format_transform_report(r, color=False)
        assert "uppercase_keys" in report
        assert "strip_whitespace" in report

    def test_changed_key_shown_with_old_and_new(self):
        r = _result({"foo": "bar"}, uppercase_keys=True)
        report = format_transform_report(r, color=False)
        assert "foo=bar" in report
        assert "FOO=bar" in report

    def test_changed_key_count_in_summary(self):
        r = _result({"A": "  hi  "}, strip_whitespace=True)
        report = format_transform_report(r, color=False)
        assert "Changed keys: 1" in report

    def test_none_shown_when_no_transforms_applied(self):
        r = _result({"A": "1"})
        report = format_transform_report(r, color=False)
        assert "(none)" in report

    def test_color_disabled_no_escape_codes(self):
        r = _result({"foo": "1"}, uppercase_keys=True)
        report = format_transform_report(r, color=False)
        assert "\033[" not in report

    def test_color_enabled_contains_escape_codes(self):
        r = _result({"foo": "1"}, uppercase_keys=True)
        report = format_transform_report(r, color=True)
        assert "\033[" in report


class TestPrintTransformReport:
    def test_prints_to_provided_file(self):
        r = _result({"A": "1"})
        buf = io.StringIO()
        print_transform_report(r, color=False, file=buf)
        assert "Transform Report" in buf.getvalue()

    def test_masked_values_shown_in_report(self):
        r = _result({"DB_PASSWORD": "s3cr3t"}, mask_sensitive=True)
        buf = io.StringIO()
        print_transform_report(r, color=False, file=buf)
        output = buf.getvalue()
        assert "DB_PASSWORD" in output
        assert "***" in output
