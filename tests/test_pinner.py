"""Tests for envdiff.pinner."""

import pytest

from envdiff.pinner import PinEntry, PinResult, pin_env


# ---------------------------------------------------------------------------
# PinEntry helpers
# ---------------------------------------------------------------------------

class TestPinEntry:
    def test_stable_entry(self):
        e = PinEntry(key="FOO", pinned_value="bar", current_value="bar")
        assert not e.is_drifted
        assert not e.is_missing

    def test_drifted_entry(self):
        e = PinEntry(key="FOO", pinned_value="bar", current_value="baz")
        assert e.is_drifted
        assert not e.is_missing

    def test_missing_entry(self):
        e = PinEntry(key="FOO", pinned_value="bar", current_value=None)
        assert e.is_missing
        assert e.is_drifted  # missing implies drifted


# ---------------------------------------------------------------------------
# pin_env — basic behaviour
# ---------------------------------------------------------------------------

class TestPinEnv:
    def test_all_stable(self):
        pinned = {"A": "1", "B": "2"}
        current = {"A": "1", "B": "2"}
        result = pin_env(pinned, current)
        assert not result.has_drift
        assert len(result.stable) == 2
        assert result.drift_count() == 0

    def test_drifted_value_detected(self):
        pinned = {"HOST": "localhost"}
        current = {"HOST": "prod.example.com"}
        result = pin_env(pinned, current)
        assert result.has_drift
        assert len(result.drifted) == 1
        assert result.drifted[0].key == "HOST"

    def test_missing_key_detected(self):
        pinned = {"SECRET": "abc"}
        current = {}
        result = pin_env(pinned, current)
        assert result.has_drift
        assert len(result.missing) == 1
        assert result.missing[0].key == "SECRET"

    def test_extra_keys_in_current_ignored(self):
        pinned = {"A": "1"}
        current = {"A": "1", "EXTRA": "ignored"}
        result = pin_env(pinned, current)
        assert not result.has_drift
        assert len(result.entries) == 1

    def test_keys_subset_filter(self):
        pinned = {"A": "1", "B": "2", "C": "3"}
        current = {"A": "1", "B": "changed", "C": "3"}
        result = pin_env(pinned, current, keys=["A", "C"])
        assert not result.has_drift
        assert len(result.entries) == 2

    def test_keys_subset_captures_drift(self):
        pinned = {"A": "1", "B": "2"}
        current = {"A": "1", "B": "999"}
        result = pin_env(pinned, current, keys=["B"])
        assert result.has_drift
        assert result.drift_count() == 1

    def test_entries_sorted_alphabetically(self):
        pinned = {"Z": "z", "A": "a", "M": "m"}
        current = {"Z": "z", "A": "a", "M": "m"}
        result = pin_env(pinned, current)
        assert [e.key for e in result.entries] == ["A", "M", "Z"]

    def test_empty_pinned_returns_empty_result(self):
        result = pin_env({}, {"FOO": "bar"})
        assert not result.has_drift
        assert result.entries == []
