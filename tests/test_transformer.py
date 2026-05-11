"""Tests for envdiff.transformer."""

from __future__ import annotations

import pytest

from envdiff.transformer import (
    TransformResult,
    transform_env,
)


def _env(**kwargs: str) -> dict:
    return dict(kwargs)


class TestTransformEnvNoOp:
    def test_no_transforms_returns_original(self):
        env = _env(FOO="bar", BAZ="qux")
        result = transform_env(env)
        assert result.transformed == env

    def test_applied_is_empty_when_no_transforms(self):
        result = transform_env(_env(A="1"))
        assert result.applied == []

    def test_has_no_changes_when_no_transforms(self):
        result = transform_env(_env(A="1"))
        assert not result.has_changes


class TestUppercaseKeys:
    def test_lowercase_keys_uppercased(self):
        result = transform_env(_env(foo="bar", baz="qux"), uppercase_keys=True)
        assert "FOO" in result.transformed
        assert "BAZ" in result.transformed

    def test_values_unchanged(self):
        result = transform_env(_env(foo="bar"), uppercase_keys=True)
        assert result.transformed["FOO"] == "bar"

    def test_applied_contains_uppercase_keys(self):
        result = transform_env(_env(foo="1"), uppercase_keys=True)
        assert "uppercase_keys" in result.applied


class TestStripWhitespace:
    def test_leading_trailing_stripped(self):
        result = transform_env(_env(FOO="  hello  "), strip_whitespace=True)
        assert result.transformed["FOO"] == "hello"

    def test_inner_whitespace_preserved(self):
        result = transform_env(_env(FOO="hello world"), strip_whitespace=True)
        assert result.transformed["FOO"] == "hello world"

    def test_applied_label_present(self):
        result = transform_env(_env(A="1"), strip_whitespace=True)
        assert "strip_whitespace" in result.applied


class TestAddPrefix:
    def test_prefix_prepended_to_all_keys(self):
        result = transform_env(_env(FOO="1", BAR="2"), add_prefix="APP_")
        assert set(result.transformed.keys()) == {"APP_FOO", "APP_BAR"}

    def test_applied_contains_prefix_label(self):
        result = transform_env(_env(A="1"), add_prefix="X_")
        assert any("add_prefix" in a for a in result.applied)


class TestRemovePrefix:
    def test_prefix_removed_when_present(self):
        result = transform_env(_env(APP_FOO="1", APP_BAR="2"), remove_prefix="APP_")
        assert "FOO" in result.transformed
        assert "BAR" in result.transformed

    def test_keys_without_prefix_unchanged(self):
        result = transform_env(_env(OTHER="x"), remove_prefix="APP_")
        assert "OTHER" in result.transformed


class TestMaskSensitive:
    def test_password_key_masked(self):
        result = transform_env(_env(DB_PASSWORD="secret123"), mask_sensitive=True)
        assert result.transformed["DB_PASSWORD"] == "***"

    def test_non_sensitive_key_unchanged(self):
        result = transform_env(_env(HOST="localhost"), mask_sensitive=True)
        assert result.transformed["HOST"] == "localhost"

    def test_custom_mask_value(self):
        result = transform_env(_env(API_TOKEN="abc"), mask_sensitive=True, mask_value="REDACTED")
        assert result.transformed["API_TOKEN"] == "REDACTED"


class TestTransformResult:
    def test_changed_keys_detects_differences(self):
        result = transform_env(_env(foo="  hi  "), strip_whitespace=True, uppercase_keys=True)
        assert "FOO" in result.changed_keys

    def test_original_preserved(self):
        env = _env(foo="bar")
        result = transform_env(env, uppercase_keys=True)
        assert result.original == env
