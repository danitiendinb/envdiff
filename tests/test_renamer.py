"""Tests for envdiff.renamer."""

import pytest
from envdiff.renamer import rename_keys, has_renames, renamed_keys


def _env(**kwargs):
    return dict(kwargs)


class TestRenameKeys:
    def test_simple_rename(self):
        env = _env(OLD_KEY="value")
        result = rename_keys(env, {"OLD_KEY": "NEW_KEY"})
        assert "NEW_KEY" in result.env
        assert "OLD_KEY" not in result.env
        assert result.env["NEW_KEY"] == "value"

    def test_renamed_list_populated(self):
        env = _env(A="1")
        result = rename_keys(env, {"A": "B"})
        assert ("A", "B") in result.renamed

    def test_has_renames_true(self):
        env = _env(A="1")
        result = rename_keys(env, {"A": "B"})
        assert has_renames(result) is True

    def test_has_renames_false_when_nothing_renamed(self):
        env = _env(A="1")
        result = rename_keys(env, {"MISSING": "B"})
        assert has_renames(result) is False

    def test_missing_old_key_goes_to_skipped(self):
        env = _env(A="1")
        result = rename_keys(env, {"GHOST": "NEW"})
        assert "GHOST" in result.skipped
        assert result.renamed == []

    def test_drop_old_false_keeps_original_key(self):
        env = _env(A="hello")
        result = rename_keys(env, {"A": "B"}, drop_old=False)
        assert "A" in result.env
        assert "B" in result.env

    def test_overwrite_false_skips_when_new_key_exists(self):
        env = _env(A="1", B="existing")
        result = rename_keys(env, {"A": "B"}, overwrite=False)
        assert result.env["B"] == "existing"
        assert "A" in result.skipped

    def test_overwrite_true_replaces_existing_new_key(self):
        env = _env(A="new_value", B="old_value")
        result = rename_keys(env, {"A": "B"}, overwrite=True)
        assert result.env["B"] == "new_value"
        assert "B" in result.overwritten

    def test_rename_to_same_key_is_noop(self):
        env = _env(A="val")
        result = rename_keys(env, {"A": "A"})
        assert result.env["A"] == "val"
        assert ("A", "A") in result.renamed

    def test_multiple_renames(self):
        env = _env(X="1", Y="2", Z="3")
        result = rename_keys(env, {"X": "A", "Y": "B", "Z": "C"})
        assert result.env == {"A": "1", "B": "2", "C": "3"}
        assert len(result.renamed) == 3

    def test_original_env_not_mutated(self):
        env = _env(OLD="v")
        original_copy = dict(env)
        rename_keys(env, {"OLD": "NEW"})
        assert env == original_copy

    def test_renamed_keys_helper(self):
        env = _env(FOO="bar")
        result = rename_keys(env, {"FOO": "BAZ"})
        assert renamed_keys(result) == [("FOO", "BAZ")]
