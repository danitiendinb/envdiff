"""Tests for envdiff.interpolator."""

from __future__ import annotations

import pytest

from envdiff.interpolator import (
    InterpolateResult,
    expanded_keys,
    has_unresolved,
    interpolate_env,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _interp(env: dict, context: dict | None = None) -> InterpolateResult:
    return interpolate_env(env, context=context)


# ---------------------------------------------------------------------------
# Basic expansion
# ---------------------------------------------------------------------------

class TestInterpolateEnvBasic:
    def test_no_references_unchanged(self):
        result = _interp({"FOO": "bar", "BAZ": "qux"})
        assert result.env == {"FOO": "bar", "BAZ": "qux"}
        assert result.expanded == {}
        assert result.unresolved == []

    def test_braced_reference_expanded(self):
        result = _interp({"BASE": "/app", "PATH": "${BASE}/bin"})
        assert result.env["PATH"] == "/app/bin"
        assert "PATH" in result.expanded

    def test_bare_reference_expanded(self):
        result = _interp({"HOST": "localhost", "URL": "http://$HOST/api"})
        assert result.env["URL"] == "http://localhost/api"
        assert "URL" in result.expanded

    def test_multiple_references_in_one_value(self):
        result = _interp({"H": "host", "P": "5432", "DSN": "${H}:${P}"})
        assert result.env["DSN"] == "host:5432"

    def test_self_referential_expansion_uses_earlier_value(self):
        # BASE defined first; PATH defined second can reference it
        result = _interp({"BASE": "/opt", "CONF": "${BASE}/conf"})
        assert result.env["CONF"] == "/opt/conf"


# ---------------------------------------------------------------------------
# Default fallback syntax  ${VAR:-default}
# ---------------------------------------------------------------------------

class TestDefaultFallback:
    def test_default_used_when_key_missing(self):
        result = _interp({"VAL": "${MISSING:-fallback}"})
        assert result.env["VAL"] == "fallback"
        assert "VAL" in result.expanded
        assert result.unresolved == []

    def test_default_not_used_when_key_present(self):
        result = _interp({"HOST": "prod", "VAL": "${HOST:-dev}"})
        assert result.env["VAL"] == "prod"

    def test_empty_default_resolves_to_empty_string(self):
        result = _interp({"VAL": "${MISSING:-}"})
        assert result.env["VAL"] == ""
        assert result.unresolved == []


# ---------------------------------------------------------------------------
# Unresolved references
# ---------------------------------------------------------------------------

class TestUnresolvedReferences:
    def test_missing_bare_ref_marked_unresolved(self):
        result = _interp({"VAL": "$GHOST"})
        assert "VAL" in result.unresolved
        assert result.env["VAL"] == "$GHOST"  # token preserved

    def test_missing_braced_ref_without_default_marked_unresolved(self):
        result = _interp({"VAL": "${GHOST}"})
        assert "VAL" in result.unresolved

    def test_has_unresolved_true(self):
        result = _interp({"X": "${NOPE}"})
        assert has_unresolved(result) is True

    def test_has_unresolved_false(self):
        result = _interp({"X": "plain"})
        assert has_unresolved(result) is False


# ---------------------------------------------------------------------------
# External context
# ---------------------------------------------------------------------------

class TestExternalContext:
    def test_context_provides_values_not_in_env(self):
        result = _interp({"URL": "${BASE}/path"}, context={"BASE": "/root"})
        assert result.env["URL"] == "/root/path"
        assert result.unresolved == []

    def test_env_overrides_context_for_later_keys(self):
        # env key BASE should shadow context BASE once resolved
        result = _interp(
            {"BASE": "/env", "URL": "${BASE}/x"},
            context={"BASE": "/ctx"},
        )
        # context is merged first; env key BASE then updates lookup
        assert result.env["URL"] == "/env/x"


# ---------------------------------------------------------------------------
# expanded_keys helper
# ---------------------------------------------------------------------------

def test_expanded_keys_returns_list():
    result = _interp({"A": "${B}", "B": "hello"})
    keys = expanded_keys(result)
    assert "A" in keys
