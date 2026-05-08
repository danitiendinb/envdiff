"""Tests for envdiff.linter."""

import pytest
from envdiff.linter import lint_env_string, LintIssue


class TestLintEnvStringValid:
    def test_clean_file_no_issues(self):
        src = "DEBUG=false\nPORT=8080\nDB_HOST=localhost\n"
        result = lint_env_string(src)
        assert not result.has_issues

    def test_comments_and_blanks_ignored(self):
        src = "# comment\n\nAPP_NAME=envdiff\n"
        result = lint_env_string(src)
        assert not result.has_issues

    def test_export_prefix_accepted(self):
        src = "export API_URL=https://example.com\n"
        result = lint_env_string(src)
        assert not result.has_issues


class TestLintEnvStringErrors:
    def test_missing_equals_is_error(self):
        result = lint_env_string("BADLINE\n")
        codes = [i.code for i in result.errors]
        assert "E001" in codes

    def test_empty_key_is_error(self):
        result = lint_env_string("=value\n")
        codes = [i.code for i in result.errors]
        assert "E002" in codes

    def test_key_with_space_is_error(self):
        result = lint_env_string("BAD KEY=value\n")
        codes = [i.code for i in result.errors]
        assert "E003" in codes


class TestLintEnvStringWarnings:
    def test_lowercase_key_is_warning(self):
        result = lint_env_string("debug=true\n")
        codes = [i.code for i in result.warnings]
        assert "W001" in codes

    def test_duplicate_key_is_warning(self):
        src = "PORT=3000\nPORT=4000\n"
        result = lint_env_string(src)
        codes = [i.code for i in result.warnings]
        assert "W002" in codes

    def test_duplicate_reports_first_line(self):
        src = "PORT=3000\nPORT=4000\n"
        result = lint_env_string(src)
        dup = next(i for i in result.warnings if i.code == "W002")
        assert "line 1" in dup.message


class TestLintEnvStringInfo:
    def test_empty_value_non_sensitive_is_info(self):
        result = lint_env_string("APP_ENV=\n")
        codes = [i.code for i in result.issues if i.severity == "info"]
        assert "I001" in codes

    def test_empty_value_sensitive_key_not_flagged(self):
        result = lint_env_string("API_TOKEN=\n")
        info_codes = [i.code for i in result.issues if i.severity == "info"]
        assert "I001" not in info_codes


class TestLintResultProperties:
    def test_errors_property_filters_correctly(self):
        result = lint_env_string("BADLINE\ndebug=x\n")
        assert all(i.severity == "error" for i in result.errors)

    def test_warnings_property_filters_correctly(self):
        result = lint_env_string("debug=x\n")
        assert all(i.severity == "warning" for i in result.warnings)

    def test_has_issues_false_when_clean(self):
        result = lint_env_string("OK=value\n")
        assert not result.has_issues
