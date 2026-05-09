"""Tests for envdiff.normalizer."""

import pytest
from envdiff.normalizer import (
    NormalizeResult,
    _normalize_key,
    _normalize_value,
    _normalize_boolean,
    normalize_env,
)


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

class TestNormalizeKey:
    def test_strips_whitespace(self):
        assert _normalize_key("  foo  ") == "FOO"

    def test_uppercases(self):
        assert _normalize_key("db_host") == "DB_HOST"

    def test_already_upper(self):
        assert _normalize_key("ALREADY") == "ALREADY"


class TestNormalizeValue:
    def test_strips_whitespace(self):
        assert _normalize_value("  hello  ") == "hello"

    def test_empty_string(self):
        assert _normalize_value("") == ""

    def test_no_change_needed(self):
        assert _normalize_value("clean") == "clean"


class TestNormalizeBoolean:
    @pytest.mark.parametrize("raw", ["1", "yes", "on", "True", "TRUE"])
    def test_truthy_values(self, raw):
        assert _normalize_boolean(raw) == "true"

    @pytest.mark.parametrize("raw", ["0", "no", "off", "False", "FALSE"])
    def test_falsy_values(self, raw):
        assert _normalize_boolean(raw) == "false"

    def test_non_boolean_unchanged(self):
        assert _normalize_boolean("maybe") == "maybe"


# ---------------------------------------------------------------------------
# Integration tests for normalize_env
# ---------------------------------------------------------------------------

class TestNormalizeEnv:
    def test_uppercase_keys_by_default(self):
        result = normalize_env({"db_host": "localhost"})
        assert "DB_HOST" in result.normalized

    def test_original_key_removed(self):
        result = normalize_env({"db_host": "localhost"})
        assert "db_host" not in result.normalized

    def test_strip_values_by_default(self):
        result = normalize_env({"KEY": "  value  "})
        assert result.normalized["KEY"] == "value"

    def test_no_uppercase_when_disabled(self):
        result = normalize_env({"lower": "v"}, uppercase_keys=False)
        assert "lower" in result.normalized

    def test_boolean_normalization_off_by_default(self):
        result = normalize_env({"FLAG": "yes"})
        assert result.normalized["FLAG"] == "yes"

    def test_boolean_normalization_enabled(self):
        result = normalize_env({"FLAG": "yes"}, normalize_booleans=True)
        assert result.normalized["FLAG"] == "true"

    def test_has_changes_when_key_uppercased(self):
        result = normalize_env({"lower_key": "val"})
        assert result.has_changes()

    def test_no_changes_when_already_normalized(self):
        result = normalize_env({"KEY": "value"})
        assert not result.has_changes()

    def test_multiple_keys(self):
        env = {"a": "1", "b": "2", "c": "3"}
        result = normalize_env(env)
        assert set(result.normalized.keys()) == {"A", "B", "C"}

    def test_empty_env(self):
        result = normalize_env({})
        assert result.normalized == {}
        assert not result.has_changes()
