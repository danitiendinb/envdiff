"""Tests for envdiff.deduplicator."""

from __future__ import annotations

import pytest

from envdiff.deduplicator import (
    DeduplicateResult,
    deduplicate_env,
    find_duplicates,
)


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------


class TestFindDuplicates:
    def test_no_duplicates_returns_empty(self):
        src = "FOO=bar\nBAZ=qux\n"
        assert find_duplicates(src) == {}

    def test_single_duplicate_detected(self):
        src = "FOO=first\nFOO=second\n"
        result = find_duplicates(src)
        assert "FOO" in result
        assert result["FOO"] == ["first", "second"]

    def test_multiple_duplicates_detected(self):
        src = "A=1\nB=2\nA=3\nB=4\nB=5\n"
        result = find_duplicates(src)
        assert result["A"] == ["1", "3"]
        assert result["B"] == ["2", "4", "5"]

    def test_comments_and_blanks_ignored(self):
        src = "# FOO=comment\n\nFOO=real\n"
        assert find_duplicates(src) == {}

    def test_export_prefix_handled(self):
        src = "export KEY=alpha\nexport KEY=beta\n"
        result = find_duplicates(src)
        assert result["KEY"] == ["alpha", "beta"]

    def test_quoted_values_stripped(self):
        src = 'SECRET="abc"\nSECRET="def"\n'
        result = find_duplicates(src)
        assert result["SECRET"] == ["abc", "def"]

    def test_line_without_equals_skipped(self):
        src = "INVALID_LINE\nFOO=bar\n"
        assert find_duplicates(src) == {}


# ---------------------------------------------------------------------------
# deduplicate_env
# ---------------------------------------------------------------------------


class TestDeduplicateEnv:
    def test_no_duplicates_result_unchanged(self):
        env = {"FOO": "bar", "BAZ": "qux"}
        src = "FOO=bar\nBAZ=qux\n"
        result = deduplicate_env(env, src)
        assert result.env == env
        assert not result.has_duplicates

    def test_has_duplicates_flag(self):
        env = {"FOO": "second"}  # parser kept last
        src = "FOO=first\nFOO=second\n"
        result = deduplicate_env(env, src)
        assert result.has_duplicates
        assert "FOO" in result.duplicate_keys

    def test_keep_last_default(self):
        env = {"FOO": "second"}
        src = "FOO=first\nFOO=second\n"
        result = deduplicate_env(env, src, keep="last")
        assert result.env["FOO"] == "second"

    def test_keep_first_overrides_value(self):
        env = {"FOO": "second"}  # parser kept last
        src = "FOO=first\nFOO=second\n"
        result = deduplicate_env(env, src, keep="first")
        assert result.env["FOO"] == "first"

    def test_no_env_string_no_duplicates_recorded(self):
        env = {"A": "1"}
        result = deduplicate_env(env)
        assert not result.has_duplicates
        assert result.env == env

    def test_duplicate_keys_sorted(self):
        src = "Z=1\nA=2\nZ=3\nA=4\n"
        env = {"Z": "3", "A": "4"}
        result = deduplicate_env(env, src)
        assert result.duplicate_keys == ["A", "Z"]
