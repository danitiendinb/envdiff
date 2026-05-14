"""Tests for envdiff.filterer."""

import pytest

from envdiff.filterer import (
    FilterResult,
    filter_by_keys,
    filter_by_pattern,
    filter_by_prefix,
    filter_empty_values,
    filter_env,
)

ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "s3cr3t",
    "APP_DEBUG": "",
    "REDIS_URL": "redis://localhost",
}


# ---------------------------------------------------------------------------
# filter_by_pattern
# ---------------------------------------------------------------------------

class TestFilterByPattern:
    def test_matches_substring(self):
        result = filter_by_pattern(ENV, "DB_")
        assert set(result.matched) == {"DB_HOST", "DB_PORT"}

    def test_case_insensitive(self):
        result = filter_by_pattern(ENV, "app")
        assert set(result.matched) == {"APP_SECRET", "APP_DEBUG"}

    def test_no_match_returns_empty(self):
        result = filter_by_pattern(ENV, "NONEXISTENT")
        assert result.matched == {}
        assert result.excluded_count == len(ENV)

    def test_invalid_pattern_raises(self):
        with pytest.raises(ValueError, match="Invalid pattern"):
            filter_by_pattern(ENV, "[invalid")

    def test_total_reflects_input_size(self):
        result = filter_by_pattern(ENV, "DB")
        assert result.total == len(ENV)


# ---------------------------------------------------------------------------
# filter_by_prefix
# ---------------------------------------------------------------------------

class TestFilterByPrefix:
    def test_basic_prefix(self):
        result = filter_by_prefix(ENV, "APP_")
        assert set(result.matched) == {"APP_SECRET", "APP_DEBUG"}

    def test_prefix_case_insensitive(self):
        result = filter_by_prefix(ENV, "db")
        assert set(result.matched) == {"DB_HOST", "DB_PORT"}

    def test_no_match(self):
        result = filter_by_prefix(ENV, "MONGO")
        assert result.matched == {}


# ---------------------------------------------------------------------------
# filter_empty_values
# ---------------------------------------------------------------------------

class TestFilterEmptyValues:
    def test_removes_empty_value(self):
        result = filter_empty_values(ENV)
        assert "APP_DEBUG" not in result.matched

    def test_non_empty_values_preserved(self):
        result = filter_empty_values(ENV)
        assert "DB_HOST" in result.matched

    def test_excluded_contains_empty_key(self):
        result = filter_empty_values(ENV)
        assert "APP_DEBUG" in result.excluded


# ---------------------------------------------------------------------------
# filter_by_keys
# ---------------------------------------------------------------------------

class TestFilterByKeys:
    def test_exact_keys_selected(self):
        result = filter_by_keys(ENV, ["DB_HOST", "REDIS_URL"])
        assert set(result.matched) == {"DB_HOST", "REDIS_URL"}

    def test_missing_keys_ignored(self):
        result = filter_by_keys(ENV, ["GHOST_KEY"])
        assert result.matched == {}

    def test_empty_key_list(self):
        result = filter_by_keys(ENV, [])
        assert result.matched == {}
        assert result.excluded_count == len(ENV)


# ---------------------------------------------------------------------------
# filter_env (combined)
# ---------------------------------------------------------------------------

class TestFilterEnv:
    def test_no_filters_returns_all(self):
        result = filter_env(ENV)
        assert result.matched == ENV

    def test_pattern_and_exclude_empty_combined(self):
        result = filter_env(ENV, pattern="APP_", exclude_empty=True)
        assert "APP_SECRET" in result.matched
        assert "APP_DEBUG" not in result.matched

    def test_prefix_filter(self):
        result = filter_env(ENV, prefix="REDIS")
        assert set(result.matched) == {"REDIS_URL"}

    def test_match_count_property(self):
        result = filter_env(ENV, prefix="DB_")
        assert result.match_count == 2
