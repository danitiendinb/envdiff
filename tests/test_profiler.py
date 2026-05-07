"""Tests for envdiff.profiler."""

import pytest
from envdiff.profiler import profile_env, _is_sensitive, _find_duplicate_values


class TestIsSensitive:
    def test_password_key(self):
        assert _is_sensitive("DB_PASSWORD") is True

    def test_token_key(self):
        assert _is_sensitive("GITHUB_TOKEN") is True

    def test_api_key(self):
        assert _is_sensitive("STRIPE_API_KEY") is True

    def test_plain_key_not_sensitive(self):
        assert _is_sensitive("APP_PORT") is False

    def test_case_insensitive(self):
        assert _is_sensitive("db_Secret") is True


class TestFindDuplicateValues:
    def test_no_duplicates(self):
        env = {"A": "1", "B": "2"}
        assert _find_duplicate_values(env) == {}

    def test_duplicate_detected(self):
        env = {"A": "same", "B": "same", "C": "other"}
        dupes = _find_duplicate_values(env)
        assert "same" in dupes
        assert set(dupes["same"]) == {"A", "B"}

    def test_empty_values_ignored(self):
        env = {"A": "", "B": ""}
        assert _find_duplicate_values(env) == {}


class TestProfileEnv:
    def test_total_keys(self):
        env = {"A": "1", "B": "2", "C": "3"}
        result = profile_env(env)
        assert result.total_keys == 3

    def test_empty_values_listed(self):
        env = {"A": "val", "B": ""}
        result = profile_env(env)
        assert "B" in result.empty_values
        assert "A" not in result.empty_values

    def test_sensitive_keys_listed(self):
        env = {"DB_PASSWORD": "secret", "PORT": "8080"}
        result = profile_env(env)
        assert "DB_PASSWORD" in result.sensitive_keys
        assert "PORT" not in result.sensitive_keys

    def test_longest_key(self):
        env = {"SHORT": "a", "MUCH_LONGER_KEY": "b"}
        result = profile_env(env)
        assert result.longest_key == "MUCH_LONGER_KEY"

    def test_longest_value_key(self):
        env = {"A": "short", "B": "a much longer value here"}
        result = profile_env(env)
        assert result.longest_value_key == "B"

    def test_empty_env(self):
        result = profile_env({})
        assert result.total_keys == 0
        assert result.longest_key == ""
        assert result.longest_value_key == ""

    def test_duplicate_values_populated(self):
        env = {"X": "dup", "Y": "dup", "Z": "unique"}
        result = profile_env(env)
        assert "dup" in result.duplicate_values
