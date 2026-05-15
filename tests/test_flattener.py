"""Tests for envdiff.flattener."""

from __future__ import annotations

import pytest

from envdiff.flattener import FlattenResult, flatten_env


# ---------------------------------------------------------------------------
# FlattenResult helpers
# ---------------------------------------------------------------------------

class TestFlattenResult:
    def test_key_count(self):
        r = FlattenResult(env={"A": "1", "B": "2"})
        assert r.key_count() == 2

    def test_has_skipped_false(self):
        r = FlattenResult(env={})
        assert not r.has_skipped()

    def test_has_skipped_true(self):
        r = FlattenResult(env={}, skipped=["deep.key"])
        assert r.has_skipped()


# ---------------------------------------------------------------------------
# flatten_env – basic cases
# ---------------------------------------------------------------------------

class TestFlattenEnvBasic:
    def test_flat_dict_unchanged_structure(self):
        result = flatten_env({"host": "localhost", "port": "5432"})
        assert result.env["HOST"] == "localhost"
        assert result.env["PORT"] == "5432"

    def test_nested_dict_uses_separator(self):
        result = flatten_env({"db": {"host": "localhost"}})
        assert "DB__HOST" in result.env
        assert result.env["DB__HOST"] == "localhost"

    def test_custom_separator(self):
        result = flatten_env({"db": {"host": "x"}}, separator="_")
        assert "DB_HOST" in result.env

    def test_prefix_prepended(self):
        result = flatten_env({"key": "val"}, prefix="APP")
        assert "APP__KEY" in result.env

    def test_none_value_becomes_empty_string(self):
        result = flatten_env({"missing": None})
        assert result.env["MISSING"] == ""

    def test_bool_true_becomes_string(self):
        result = flatten_env({"flag": True})
        assert result.env["FLAG"] == "true"

    def test_bool_false_becomes_string(self):
        result = flatten_env({"flag": False})
        assert result.env["FLAG"] == "false"

    def test_integer_value_coerced(self):
        result = flatten_env({"port": 8080})
        assert result.env["PORT"] == "8080"

    def test_list_indexed_keys(self):
        result = flatten_env({"hosts": ["a", "b"]})
        assert result.env["HOSTS__0"] == "a"
        assert result.env["HOSTS__1"] == "b"

    def test_empty_nested_dict(self):
        result = flatten_env({"section": {}})
        assert result.env == {}

    def test_empty_top_level(self):
        result = flatten_env({})
        assert result.env == {}
        assert result.key_count() == 0


# ---------------------------------------------------------------------------
# flatten_env – depth limiting
# ---------------------------------------------------------------------------

class TestFlattenEnvMaxDepth:
    def test_exceeding_max_depth_skips_key(self):
        deep = {"a": {"b": {"c": {"d": "val"}}}}
        result = flatten_env(deep, max_depth=2)
        assert result.has_skipped()

    def test_within_max_depth_not_skipped(self):
        deep = {"a": {"b": "val"}}
        result = flatten_env(deep, max_depth=5)
        assert not result.has_skipped()
        assert result.env["A__B"] == "val"

    def test_skipped_paths_recorded(self):
        deep = {"x": {"y": {"z": "deep"}}}
        result = flatten_env(deep, max_depth=1)
        assert len(result.skipped) >= 1
