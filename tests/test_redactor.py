"""Tests for envdiff.redactor."""

import pytest

from envdiff.redactor import (
    DEFAULT_MASK,
    RedactResult,
    is_sensitive_key,
    redact_env,
)


# ---------------------------------------------------------------------------
# is_sensitive_key
# ---------------------------------------------------------------------------

class TestIsSensitiveKey:
    def test_password_fragment(self):
        assert is_sensitive_key("DB_PASSWORD") is True

    def test_token_fragment(self):
        assert is_sensitive_key("GITHUB_TOKEN") is True

    def test_api_key_fragment(self):
        assert is_sensitive_key("STRIPE_API_KEY") is True

    def test_secret_fragment(self):
        assert is_sensitive_key("APP_SECRET") is True

    def test_plain_key_not_sensitive(self):
        assert is_sensitive_key("APP_ENV") is False

    def test_case_insensitive(self):
        assert is_sensitive_key("db_passwd") is True


# ---------------------------------------------------------------------------
# redact_env
# ---------------------------------------------------------------------------

class TestRedactEnv:
    def test_non_sensitive_keys_unchanged(self):
        env = {"APP_ENV": "production", "PORT": "8080"}
        result = redact_env(env)
        assert result.redacted == env
        assert result.redacted_keys == []

    def test_sensitive_key_replaced_with_mask(self):
        env = {"DB_PASSWORD": "s3cr3t", "HOST": "localhost"}
        result = redact_env(env)
        assert result.redacted["DB_PASSWORD"] == DEFAULT_MASK
        assert result.redacted["HOST"] == "localhost"

    def test_redacted_keys_reported(self):
        env = {"API_KEY": "abc", "TOKEN": "xyz", "NAME": "app"}
        result = redact_env(env)
        assert set(result.redacted_keys) == {"API_KEY", "TOKEN"}

    def test_redaction_count(self):
        env = {"SECRET": "x", "AUTH_TOKEN": "y", "DEBUG": "true"}
        result = redact_env(env)
        assert result.redaction_count == 2

    def test_custom_mask(self):
        env = {"DB_PASSWORD": "hunter2"}
        result = redact_env(env, mask="<hidden>")
        assert result.redacted["DB_PASSWORD"] == "<hidden>"

    def test_preserve_length(self):
        env = {"DB_PASSWORD": "hunter2"}
        result = redact_env(env, preserve_length=True)
        assert result.redacted["DB_PASSWORD"] == "*" * len("hunter2")

    def test_extra_keys_redacted(self):
        env = {"MY_CUSTOM": "value", "OTHER": "keep"}
        result = redact_env(env, extra_keys=["MY_CUSTOM"])
        assert result.redacted["MY_CUSTOM"] == DEFAULT_MASK
        assert result.redacted["OTHER"] == "keep"

    def test_extra_keys_case_insensitive(self):
        env = {"MY_CUSTOM": "value"}
        result = redact_env(env, extra_keys=["my_custom"])
        assert result.redacted["MY_CUSTOM"] == DEFAULT_MASK

    def test_empty_env(self):
        result = redact_env({})
        assert result.redacted == {}
        assert result.redaction_count == 0

    def test_original_env_not_mutated(self):
        env = {"DB_PASSWORD": "secret"}
        redact_env(env)
        assert env["DB_PASSWORD"] == "secret"
