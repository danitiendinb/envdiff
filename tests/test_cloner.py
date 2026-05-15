"""Tests for envdiff.cloner."""

import pytest

from envdiff.cloner import CloneResult, clone_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(**kwargs: str):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# CloneResult properties
# ---------------------------------------------------------------------------

class TestCloneResult:
    def test_has_changes_false_when_plain_clone(self):
        r = CloneResult(env={"A": "1"})
        assert not r.has_changes

    def test_has_changes_true_when_remapped(self):
        r = CloneResult(env={"B": "1"}, remapped=["A"])
        assert r.has_changes

    def test_counts_default_to_zero(self):
        r = CloneResult(env={})
        assert r.remapped_count == 0
        assert r.overridden_count == 0
        assert r.dropped_count == 0


# ---------------------------------------------------------------------------
# Basic cloning
# ---------------------------------------------------------------------------

def test_plain_clone_copies_all_keys():
    src = _env(HOST="localhost", PORT="5432")
    result = clone_env(src)
    assert result.env == src
    assert not result.has_changes


def test_plain_clone_is_independent_copy():
    src = _env(HOST="localhost")
    result = clone_env(src)
    result.env["HOST"] = "changed"
    assert src["HOST"] == "localhost"


# ---------------------------------------------------------------------------
# drop_keys
# ---------------------------------------------------------------------------

def test_drop_keys_removes_specified_keys():
    src = _env(A="1", B="2", C="3")
    result = clone_env(src, drop_keys=["B"])
    assert "B" not in result.env
    assert result.dropped == ["B"]
    assert result.dropped_count == 1


def test_drop_keys_ignores_absent_keys():
    src = _env(A="1")
    result = clone_env(src, drop_keys=["MISSING"])
    assert result.env == {"A": "1"}
    assert result.dropped == []


def test_drop_multiple_keys():
    src = _env(A="1", B="2", C="3")
    result = clone_env(src, drop_keys=["A", "C"])
    assert result.env == {"B": "2"}
    assert result.dropped_count == 2


# ---------------------------------------------------------------------------
# key_map
# ---------------------------------------------------------------------------

def test_key_map_renames_key():
    src = _env(OLD_HOST="localhost")
    result = clone_env(src, key_map={"OLD_HOST": "HOST"})
    assert "HOST" in result.env
    assert "OLD_HOST" not in result.env
    assert result.remapped == ["OLD_HOST"]


def test_key_map_ignores_absent_source_keys():
    src = _env(A="1")
    result = clone_env(src, key_map={"NONEXISTENT": "X"})
    assert result.env == {"A": "1"}
    assert result.remapped == []


def test_key_map_and_drop_interact_correctly():
    """Dropped keys should not appear even if also in key_map."""
    src = _env(A="1", B="2")
    result = clone_env(src, key_map={"A": "ALPHA"}, drop_keys=["A"])
    assert "ALPHA" not in result.env
    assert "A" not in result.env
    assert result.dropped == ["A"]
    assert result.remapped == []


# ---------------------------------------------------------------------------
# overrides
# ---------------------------------------------------------------------------

def test_overrides_replace_existing_value():
    src = _env(HOST="old")
    result = clone_env(src, overrides={"HOST": "new"})
    assert result.env["HOST"] == "new"
    assert "HOST" in result.overridden


def test_overrides_add_new_key():
    src = _env(A="1")
    result = clone_env(src, overrides={"NEW_KEY": "injected"})
    assert result.env["NEW_KEY"] == "injected"
    assert result.overridden_count == 1


# ---------------------------------------------------------------------------
# Combined transformations
# ---------------------------------------------------------------------------

def test_combined_remap_override_drop():
    src = _env(DB_HOST="old-host", DB_PORT="5432", DEBUG="true")
    result = clone_env(
        src,
        key_map={"DB_HOST": "HOST"},
        overrides={"HOST": "prod-host"},
        drop_keys=["DEBUG"],
    )
    assert result.env["HOST"] == "prod-host"
    assert result.env["DB_PORT"] == "5432"
    assert "DEBUG" not in result.env
    assert result.has_changes
