"""Tests for envdiff.merger."""

from __future__ import annotations

import pytest

from envdiff.merger import MergeResult, merge_envs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"PORT": "5433", "DB": "mydb"}
ENV_C = {"PORT": "5434", "LOG_LEVEL": "info"}


# ---------------------------------------------------------------------------
# Basic merging
# ---------------------------------------------------------------------------

class TestMergeEnvs:
    def test_single_env_returned_unchanged(self):
        result = merge_envs(ENV_A)
        assert result.merged == ENV_A
        assert not result.has_conflicts

    def test_empty_args_returns_empty(self):
        result = merge_envs()
        assert result.merged == {}
        assert not result.has_conflicts

    def test_two_envs_no_overlap(self):
        result = merge_envs({"A": "1"}, {"B": "2"})
        assert result.merged == {"A": "1", "B": "2"}
        assert not result.has_conflicts

    def test_later_env_wins_on_conflict(self):
        result = merge_envs(ENV_A, ENV_B)
        assert result.merged["PORT"] == "5433"

    def test_non_conflicting_keys_preserved(self):
        result = merge_envs(ENV_A, ENV_B)
        assert result.merged["HOST"] == "localhost"
        assert result.merged["DB"] == "mydb"

    def test_three_way_merge_last_wins(self):
        result = merge_envs(ENV_A, ENV_B, ENV_C)
        assert result.merged["PORT"] == "5434"
        assert result.merged["LOG_LEVEL"] == "info"
        assert result.merged["DB"] == "mydb"
        assert result.merged["HOST"] == "localhost"


# ---------------------------------------------------------------------------
# Conflict tracking
# ---------------------------------------------------------------------------

class TestConflictTracking:
    def test_conflict_recorded_for_overwritten_key(self):
        result = merge_envs(ENV_A, ENV_B)
        assert "PORT" in result.conflicts

    def test_conflict_stores_overwritten_value(self):
        result = merge_envs(ENV_A, ENV_B)
        overwritten_values = [v for _, v in result.conflicts["PORT"]]
        assert "5432" in overwritten_values

    def test_no_conflict_when_tracking_disabled(self):
        result = merge_envs(ENV_A, ENV_B, track_conflicts=False)
        assert not result.has_conflicts
        # Merge result should still be correct
        assert result.merged["PORT"] == "5433"

    def test_multiple_conflicts_same_key(self):
        result = merge_envs(ENV_A, ENV_B, ENV_C)
        # PORT is overwritten twice
        assert len(result.conflicts["PORT"]) == 2

    def test_has_conflicts_property_false_when_clean(self):
        result = merge_envs({"X": "1"}, {"Y": "2"})
        assert result.has_conflicts is False

    def test_has_conflicts_property_true_when_dirty(self):
        result = merge_envs(ENV_A, ENV_B)
        assert result.has_conflicts is True
