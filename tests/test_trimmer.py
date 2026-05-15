"""Tests for envdiff.trimmer."""
from __future__ import annotations

import pytest

from envdiff.trimmer import TrimResult, trim_by_prefix, trim_to_reference


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(**kwargs: str) -> dict:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# TrimResult properties
# ---------------------------------------------------------------------------

class TestTrimResult:
    def test_removal_count(self):
        r = TrimResult(
            original={"A": "1", "B": "2"},
            trimmed={"A": "1"},
            removed_keys=["B"],
        )
        assert r.removal_count == 1

    def test_has_removals_true(self):
        r = TrimResult(original={"A": "1"}, trimmed={}, removed_keys=["A"])
        assert r.has_removals is True

    def test_has_removals_false(self):
        r = TrimResult(original={"A": "1"}, trimmed={"A": "1"}, removed_keys=[])
        assert r.has_removals is False


# ---------------------------------------------------------------------------
# trim_to_reference
# ---------------------------------------------------------------------------

class TestTrimToReference:
    def test_keeps_only_reference_keys(self):
        env = _env(DB_HOST="localhost", DB_PORT="5432", UNUSED="yes")
        result = trim_to_reference(env, {"DB_HOST", "DB_PORT"})
        assert result.trimmed == {"DB_HOST": "localhost", "DB_PORT": "5432"}

    def test_removed_keys_sorted(self):
        env = _env(Z="z", A="a", M="m")
        result = trim_to_reference(env, {"A"})
        assert result.removed_keys == ["M", "Z"]

    def test_no_removals_when_all_in_reference(self):
        env = _env(X="1", Y="2")
        result = trim_to_reference(env, {"X", "Y", "Z"})
        assert result.has_removals is False
        assert result.trimmed == env

    def test_empty_env_returns_empty(self):
        result = trim_to_reference({}, {"A", "B"})
        assert result.trimmed == {}
        assert result.removed_keys == []

    def test_ignore_case_matches(self):
        env = _env(db_host="localhost", EXTRA="drop")
        result = trim_to_reference(env, {"DB_HOST"}, ignore_case=True)
        assert "db_host" in result.trimmed
        assert "EXTRA" in result.removed_keys

    def test_original_preserved(self):
        env = _env(A="1", B="2")
        result = trim_to_reference(env, {"A"})
        assert result.original == {"A": "1", "B": "2"}


# ---------------------------------------------------------------------------
# trim_by_prefix
# ---------------------------------------------------------------------------

class TestTrimByPrefix:
    def test_keeps_matching_prefix(self):
        env = _env(DB_HOST="h", DB_PORT="p", APP_NAME="n", UNRELATED="x")
        result = trim_by_prefix(env, ["DB", "APP"])
        assert set(result.trimmed) == {"DB_HOST", "DB_PORT", "APP_NAME"}

    def test_removes_keys_without_delimiter(self):
        env = _env(NOPREFIX="val", DB_HOST="h")
        result = trim_by_prefix(env, ["DB"])
        assert "NOPREFIX" in result.removed_keys

    def test_custom_delimiter(self):
        env = {"DB.HOST": "h", "APP.NAME": "n", "OTHER": "o"}
        result = trim_by_prefix(env, ["DB"], delimiter=".")
        assert set(result.trimmed) == {"DB.HOST"}

    def test_ignore_case_prefix(self):
        env = _env(db_host="h", APP_NAME="n")
        result = trim_by_prefix(env, ["DB"], ignore_case=True)
        assert "db_host" in result.trimmed
        assert "APP_NAME" in result.removed_keys

    def test_empty_allowed_prefixes_removes_all(self):
        env = _env(DB_HOST="h", APP_NAME="n")
        result = trim_by_prefix(env, [])
        assert result.trimmed == {}
        assert result.removal_count == 2
