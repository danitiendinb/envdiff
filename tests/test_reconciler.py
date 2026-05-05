"""Tests for envdiff.reconciler."""

import pytest
from envdiff.reconciler import (
    reconcile_missing,
    reconcile_overrides,
    generate_patch,
    apply_patch,
)


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


class TestReconcileMissing:
    def test_adds_missing_keys_with_empty_fill(self):
        result = reconcile_missing(BASE, TARGET)
        assert "DEBUG" in result
        assert result["DEBUG"] == ""

    def test_existing_target_keys_preserved(self):
        result = reconcile_missing(BASE, TARGET)
        assert result["HOST"] == "prod.example.com"
        assert result["SECRET"] == "abc123"

    def test_custom_fill_value(self):
        result = reconcile_missing(BASE, TARGET, fill_value="CHANGEME")
        assert result["DEBUG"] == "CHANGEME"

    def test_no_missing_keys(self):
        result = reconcile_missing(BASE, BASE)
        assert result == BASE


class TestReconcileOverrides:
    def test_override_wins(self):
        overrides = {"HOST": "staging.example.com"}
        result = reconcile_overrides(BASE, overrides)
        assert result["HOST"] == "staging.example.com"

    def test_base_keys_kept(self):
        result = reconcile_overrides(BASE, {})
        assert result == BASE

    def test_new_keys_added(self):
        result = reconcile_overrides(BASE, {"NEW_KEY": "value"})
        assert result["NEW_KEY"] == "value"
        assert "HOST" in result


class TestGenerateAndApplyPatch:
    def test_patch_captures_changes(self):
        patch = generate_patch(BASE, TARGET)
        assert patch["HOST"] == "prod.example.com"

    def test_patch_marks_deletions_as_none(self):
        patch = generate_patch(BASE, TARGET)
        assert patch["DEBUG"] is None

    def test_patch_captures_additions(self):
        patch = generate_patch(BASE, TARGET)
        assert patch["SECRET"] == "abc123"

    def test_unchanged_keys_not_in_patch(self):
        patch = generate_patch(BASE, TARGET)
        assert "PORT" not in patch

    def test_apply_patch_roundtrip(self):
        patch = generate_patch(BASE, TARGET)
        result = apply_patch(BASE, patch)
        assert result == TARGET

    def test_apply_patch_empty(self):
        result = apply_patch(BASE, {})
        assert result == BASE
