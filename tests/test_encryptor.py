"""Tests for envdiff.encryptor."""

import pytest

from envdiff.encryptor import (
    EncryptResult,
    decrypt_env,
    encrypt_env,
    is_sensitive_key,
)


# ---------------------------------------------------------------------------
# is_sensitive_key
# ---------------------------------------------------------------------------

class TestIsSensitiveKey:
    def test_password_fragment(self):
        assert is_sensitive_key("DB_PASSWORD") is True

    def test_token_fragment(self):
        assert is_sensitive_key("AUTH_TOKEN") is True

    def test_api_key_fragment(self):
        assert is_sensitive_key("STRIPE_API_KEY") is True

    def test_secret_fragment(self):
        assert is_sensitive_key("APP_SECRET") is True

    def test_private_fragment(self):
        assert is_sensitive_key("PRIVATE_KEY") is True

    def test_plain_key_not_sensitive(self):
        assert is_sensitive_key("APP_ENV") is False

    def test_case_insensitive(self):
        assert is_sensitive_key("db_password") is True


# ---------------------------------------------------------------------------
# encrypt_env / decrypt_env round-trip
# ---------------------------------------------------------------------------

class TestEncryptEnv:
    def _env(self):
        return {
            "APP_ENV": "production",
            "DB_PASSWORD": "s3cr3t",
            "AUTH_TOKEN": "tok_abc123",
        }

    def test_sensitive_keys_are_encrypted(self):
        result = encrypt_env(self._env(), passphrase="pass")
        assert result.encrypted["DB_PASSWORD"].startswith("enc:")
        assert result.encrypted["AUTH_TOKEN"].startswith("enc:")

    def test_non_sensitive_key_unchanged(self):
        result = encrypt_env(self._env(), passphrase="pass")
        assert result.encrypted["APP_ENV"] == "production"

    def test_encrypted_keys_list(self):
        result = encrypt_env(self._env(), passphrase="pass")
        assert set(result.encrypted_keys) == {"DB_PASSWORD", "AUTH_TOKEN"}

    def test_count_matches_encrypted_keys(self):
        result = encrypt_env(self._env(), passphrase="pass")
        assert result.count == 2

    def test_round_trip_restores_original(self):
        original = self._env()
        result = encrypt_env(original, passphrase="mypassphrase")
        restored = decrypt_env(result.encrypted, passphrase="mypassphrase")
        assert restored == original

    def test_wrong_passphrase_does_not_restore(self):
        result = encrypt_env(self._env(), passphrase="correct")
        restored = decrypt_env(result.encrypted, passphrase="wrong")
        assert restored["DB_PASSWORD"] != "s3cr3t"

    def test_only_sensitive_false_encrypts_all(self):
        result = encrypt_env(self._env(), passphrase="pass", only_sensitive=False)
        assert all(v.startswith("enc:") for v in result.encrypted.values())

    def test_explicit_keys_override(self):
        result = encrypt_env(self._env(), passphrase="pass", keys=["APP_ENV"])
        assert result.encrypted["APP_ENV"].startswith("enc:")
        assert not result.encrypted["DB_PASSWORD"].startswith("enc:")

    def test_already_encrypted_value_not_double_encrypted(self):
        env = {"DB_PASSWORD": "enc:alreadyencoded"}
        result = encrypt_env(env, passphrase="pass")
        assert result.encrypted["DB_PASSWORD"] == "enc:alreadyencoded"
        assert result.count == 0

    def test_empty_env_returns_empty(self):
        result = encrypt_env({}, passphrase="pass")
        assert result.encrypted == {}
        assert result.count == 0
