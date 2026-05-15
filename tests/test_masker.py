"""Tests for envdiff.masker."""
import pytest
from envdiff.masker import is_sensitive_key, mask_env, MaskResult


class TestIsSensitiveKey:
    def test_password_fragment(self):
        assert is_sensitive_key("DB_PASSWORD") is True

    def test_token_fragment(self):
        assert is_sensitive_key("GITHUB_TOKEN") is True

    def test_api_key_fragment(self):
        assert is_sensitive_key("STRIPE_API_KEY") is True

    def test_secret_fragment(self):
        assert is_sensitive_key("APP_SECRET") is True

    def test_auth_fragment(self):
        assert is_sensitive_key("AUTH_HEADER") is True

    def test_plain_key_not_sensitive(self):
        assert is_sensitive_key("APP_ENV") is False

    def test_case_insensitive(self):
        assert is_sensitive_key("db_passwd") is True


class TestMaskEnv:
    def _env(self):
        return {
            "APP_ENV": "production",
            "DB_PASSWORD": "s3cr3t",
            "GITHUB_TOKEN": "ghp_abc123",
            "PORT": "8080",
        }

    def test_sensitive_keys_masked(self):
        result = mask_env(self._env())
        assert result.masked["DB_PASSWORD"] == "***"
        assert result.masked["GITHUB_TOKEN"] == "***"

    def test_plain_keys_unchanged(self):
        result = mask_env(self._env())
        assert result.masked["APP_ENV"] == "production"
        assert result.masked["PORT"] == "8080"

    def test_mask_count(self):
        result = mask_env(self._env())
        assert result.mask_count == 2

    def test_has_masked_true(self):
        result = mask_env(self._env())
        assert result.has_masked is True

    def test_has_masked_false_when_no_sensitive(self):
        result = mask_env({"APP_ENV": "dev", "PORT": "3000"})
        assert result.has_masked is False

    def test_masked_keys_sorted(self):
        result = mask_env(self._env())
        assert result.masked_keys == sorted(result.masked_keys)

    def test_custom_mask_string(self):
        result = mask_env(self._env(), mask="[REDACTED]")
        assert result.masked["DB_PASSWORD"] == "[REDACTED]"

    def test_visible_chars_prefix_kept(self):
        result = mask_env(self._env(), visible_chars=2)
        assert result.masked["DB_PASSWORD"] == "s3***"

    def test_visible_chars_empty_value_still_masked(self):
        result = mask_env({"DB_PASSWORD": ""}, visible_chars=3)
        assert result.masked["DB_PASSWORD"] == "***"

    def test_extra_keys_treated_as_sensitive(self):
        result = mask_env({"MY_CUSTOM": "val", "OTHER": "x"}, extra_keys=["MY_CUSTOM"])
        assert result.masked["MY_CUSTOM"] == "***"
        assert result.masked["OTHER"] == "x"

    def test_original_preserved(self):
        env = self._env()
        result = mask_env(env)
        assert result.original == env
        assert result.original is not result.masked

    def test_empty_env(self):
        result = mask_env({})
        assert result.masked == {}
        assert result.mask_count == 0
