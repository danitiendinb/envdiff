"""Tests for envdiff.auditor."""

import pytest
from envdiff.auditor import (
    AuditIssue,
    AuditResult,
    audit_env,
    _is_sensitive_key,
    _check_empty_value,
    _check_weak_default,
    _check_whitespace_value,
    _check_key_naming,
)


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

class TestIsSensitiveKey:
    def test_password_fragment(self):
        assert _is_sensitive_key("DB_PASSWORD") is True

    def test_token_fragment(self):
        assert _is_sensitive_key("GITHUB_TOKEN") is True

    def test_non_sensitive(self):
        assert _is_sensitive_key("APP_PORT") is False

    def test_case_insensitive(self):
        assert _is_sensitive_key("stripe_api_key") is True


class TestCheckEmptyValue:
    def test_empty_sensitive_key_is_error(self):
        issues = _check_empty_value("DB_PASSWORD", "")
        assert len(issues) == 1
        assert issues[0].severity == "error"

    def test_empty_non_sensitive_key_no_issue(self):
        issues = _check_empty_value("APP_NAME", "")
        assert issues == []

    def test_non_empty_sensitive_key_no_issue(self):
        issues = _check_empty_value("DB_PASSWORD", "s3cur3")
        assert issues == []


class TestCheckWeakDefault:
    def test_weak_value_on_sensitive_key(self):
        issues = _check_weak_default("API_SECRET", "changeme")
        assert len(issues) == 1
        assert issues[0].severity == "warning"

    def test_weak_value_case_insensitive(self):
        issues = _check_weak_default("AUTH_TOKEN", "SECRET")
        assert len(issues) == 1

    def test_non_sensitive_key_ignored(self):
        issues = _check_weak_default("LOG_LEVEL", "secret")
        assert issues == []

    def test_strong_value_no_issue(self):
        issues = _check_weak_default("DB_PASSWORD", "xK9#mQ2!")
        assert issues == []


class TestCheckWhitespace:
    def test_leading_space(self):
        issues = _check_whitespace_value("KEY", " value")
        assert len(issues) == 1
        assert issues[0].severity == "warning"

    def test_trailing_space(self):
        issues = _check_whitespace_value("KEY", "value ")
        assert len(issues) == 1

    def test_clean_value_no_issue(self):
        issues = _check_whitespace_value("KEY", "value")
        assert issues == []


class TestCheckKeyNaming:
    def test_valid_upper_snake_case(self):
        assert _check_key_naming("APP_PORT") == []

    def test_lowercase_key_warns(self):
        issues = _check_key_naming("app_port")
        assert len(issues) == 1
        assert issues[0].severity == "warning"

    def test_mixed_case_warns(self):
        issues = _check_key_naming("AppPort")
        assert len(issues) == 1


class TestAuditEnv:
    def test_clean_env_no_issues(self):
        env = {"APP_PORT": "8080", "LOG_LEVEL": "info"}
        result = audit_env(env)
        assert not result.has_issues

    def test_multiple_issues_detected(self):
        env = {
            "db_password": "changeme",
            "API_TOKEN": "",
        }
        result = audit_env(env)
        assert result.has_issues
        assert len(result.errors) >= 1
        assert len(result.warnings) >= 1

    def test_audit_result_properties(self):
        result = AuditResult(issues=[
            AuditIssue(key="X", severity="error", message="e"),
            AuditIssue(key="Y", severity="warning", message="w"),
        ])
        assert result.has_issues
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
