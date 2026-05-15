"""Tests for envdiff.scoper."""
import pytest
from envdiff.scoper import ScopeResult, scope_env


def _env(**kwargs: str):
    return dict(kwargs)


class TestScopeResult:
    def test_included_count(self):
        r = ScopeResult(scoped={"A": "1"}, excluded={"B": "2", "C": "3"}, scope_name="s", prefixes=["A"])
        assert r.included_count == 1

    def test_excluded_count(self):
        r = ScopeResult(scoped={"A": "1"}, excluded={"B": "2", "C": "3"}, scope_name="s", prefixes=["A"])
        assert r.excluded_count == 2

    def test_has_excluded_true(self):
        r = ScopeResult(scoped={}, excluded={"X": "y"}, scope_name="s", prefixes=[])
        assert r.has_excluded is True

    def test_has_excluded_false(self):
        r = ScopeResult(scoped={"A": "1"}, excluded={}, scope_name="s", prefixes=["A"])
        assert r.has_excluded is False


class TestScopeEnvBasic:
    def test_no_prefixes_excludes_all(self):
        env = _env(APP_HOST="localhost", DB_URL="pg://")
        result = scope_env(env, prefixes=[])
        assert result.scoped == {}
        assert result.excluded == env

    def test_matching_prefix_included(self):
        env = _env(APP_HOST="localhost", APP_PORT="8080", DB_URL="pg://")
        result = scope_env(env, prefixes=["APP_"])
        assert "APP_HOST" in result.scoped
        assert "APP_PORT" in result.scoped
        assert "DB_URL" in result.excluded

    def test_non_matching_key_excluded(self):
        env = _env(DB_URL="pg://", DB_PASS="secret")
        result = scope_env(env, prefixes=["APP_"])
        assert result.scoped == {}
        assert set(result.excluded.keys()) == {"DB_URL", "DB_PASS"}

    def test_scope_name_stored(self):
        result = scope_env({}, prefixes=["X_"], scope_name="production")
        assert result.scope_name == "production"

    def test_prefixes_stored(self):
        result = scope_env({}, prefixes=["A_", "B_"])
        assert result.prefixes == ["A_", "B_"]


class TestScopeEnvCaseSensitivity:
    def test_case_insensitive_by_default(self):
        env = _env(app_host="localhost", DB_URL="pg://")
        result = scope_env(env, prefixes=["APP_"])
        assert "app_host" in result.scoped

    def test_case_sensitive_no_match(self):
        env = _env(app_host="localhost")
        result = scope_env(env, prefixes=["APP_"], case_sensitive=True)
        assert result.scoped == {}
        assert "app_host" in result.excluded

    def test_case_sensitive_exact_match(self):
        env = _env(APP_HOST="localhost")
        result = scope_env(env, prefixes=["APP_"], case_sensitive=True)
        assert "APP_HOST" in result.scoped


class TestScopeEnvStripPrefix:
    def test_strip_prefix_removes_prefix(self):
        env = _env(APP_HOST="localhost", APP_PORT="8080")
        result = scope_env(env, prefixes=["APP_"], strip_prefix=True)
        assert "HOST" in result.scoped
        assert "PORT" in result.scoped
        assert result.scoped["HOST"] == "localhost"

    def test_strip_prefix_false_keeps_original_key(self):
        env = _env(APP_HOST="localhost")
        result = scope_env(env, prefixes=["APP_"], strip_prefix=False)
        assert "APP_HOST" in result.scoped

    def test_strip_prefix_without_trailing_underscore(self):
        env = _env(APPHOST="localhost")
        result = scope_env(env, prefixes=["APP"], strip_prefix=True)
        # prefix "APP" stripped, no leading underscore left
        assert "HOST" in result.scoped

    def test_strip_prefix_empty_remainder_keeps_original(self):
        env = _env(APP="value")
        result = scope_env(env, prefixes=["APP"], strip_prefix=True)
        # stripping "APP" leaves "", fallback to original key
        assert "APP" in result.scoped

    def test_multiple_prefixes_each_stripped_correctly(self):
        env = _env(DB_HOST="pg", CACHE_HOST="redis")
        result = scope_env(env, prefixes=["DB_", "CACHE_"], strip_prefix=True)
        assert "HOST" in result.scoped
        # both keys strip to HOST; last writer wins in dict
        assert result.included_count >= 1
