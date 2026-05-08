"""Tests for envdiff.sorter."""

import pytest

from envdiff.sorter import (
    SortResult,
    _extract_prefix,
    sort_alphabetically,
    sort_by_prefix,
    sort_env,
)


# ---------------------------------------------------------------------------
# _extract_prefix
# ---------------------------------------------------------------------------

class TestExtractPrefix:
    def test_key_with_underscore(self):
        assert _extract_prefix("DB_HOST") == "DB"

    def test_key_without_underscore(self):
        assert _extract_prefix("PORT") == ""

    def test_multiple_underscores_returns_first_segment(self):
        assert _extract_prefix("AWS_S3_BUCKET") == "AWS"

    def test_empty_key(self):
        assert _extract_prefix("") == ""


# ---------------------------------------------------------------------------
# sort_alphabetically
# ---------------------------------------------------------------------------

class TestSortAlphabetically:
    def _env(self):
        return {"PORT": "8080", "APP_ENV": "prod", "APP_NAME": "myapp", "DB_HOST": "localhost"}

    def test_keys_are_sorted(self):
        result = sort_alphabetically(self._env())
        assert list(result.sorted_env.keys()) == ["APP_ENV", "APP_NAME", "DB_HOST", "PORT"]

    def test_values_preserved(self):
        result = sort_alphabetically(self._env())
        assert result.sorted_env["PORT"] == "8080"

    def test_groups_created_by_prefix(self):
        result = sort_alphabetically(self._env())
        assert "APP" in result.groups
        assert "DB" in result.groups
        assert set(result.groups["APP"]) == {"APP_ENV", "APP_NAME"}

    def test_empty_env(self):
        result = sort_alphabetically({})
        assert result.sorted_env == {}
        assert result.groups == {}


# ---------------------------------------------------------------------------
# sort_by_prefix
# ---------------------------------------------------------------------------

class TestSortByPrefix:
    def _env(self):
        return {
            "DB_HOST": "localhost",
            "APP_NAME": "myapp",
            "APP_ENV": "prod",
            "PORT": "8080",
        }

    def test_groups_in_prefix_order(self):
        result = sort_by_prefix(self._env(), prefix_order=["DB", "APP"])
        names = result.group_names()
        assert names.index("DB") < names.index("APP")

    def test_remaining_groups_appended(self):
        result = sort_by_prefix(self._env(), prefix_order=["DB"])
        names = result.group_names()
        assert "DB" in names
        assert "APP" in names
        assert "" in names  # PORT has no prefix

    def test_keys_within_group_sorted(self):
        result = sort_by_prefix(self._env())
        assert result.groups["APP"] == ["APP_ENV", "APP_NAME"]

    def test_no_prefix_order_sorts_groups_alpha(self):
        result = sort_by_prefix(self._env())
        names = result.group_names()
        assert names == sorted(names)


# ---------------------------------------------------------------------------
# sort_env (dispatcher)
# ---------------------------------------------------------------------------

class TestSortEnv:
    def test_default_mode_is_alpha(self):
        env = {"Z": "1", "A": "2"}
        result = sort_env(env)
        assert list(result.sorted_env.keys()) == ["A", "Z"]

    def test_prefix_mode_dispatches_correctly(self):
        env = {"B_X": "1", "A_Y": "2"}
        result = sort_env(env, mode="prefix", prefix_order=["B"])
        names = result.group_names()
        assert names[0] == "B"

    def test_unknown_mode_falls_back_to_alpha(self):
        env = {"Z": "1", "A": "2"}
        result = sort_env(env, mode="unknown")
        assert list(result.sorted_env.keys()) == ["A", "Z"]
