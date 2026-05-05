"""Tests for envdiff.validator module."""

import pytest
from envdiff.validator import validate_env, ValidationResult


SAMPLE_ENV = {
    "APP_NAME": "myapp",
    "PORT": "8080",
    "DEBUG": "true",
    "RATIO": "0.75",
}


class TestValidateEnvMissingRequired:
    def test_all_present_no_errors(self):
        schema = {"APP_NAME": "str", "PORT": "int"}
        result = validate_env(SAMPLE_ENV, schema)
        assert result.is_valid
        assert result.missing_required == []

    def test_missing_required_key_reported(self):
        schema = {"APP_NAME": "str", "DB_URL": "str"}
        result = validate_env(SAMPLE_ENV, schema)
        assert not result.is_valid
        assert "DB_URL" in result.missing_required

    def test_multiple_missing_keys(self):
        schema = {"MISSING_A": None, "MISSING_B": None}
        result = validate_env(SAMPLE_ENV, schema)
        assert set(result.missing_required) == {"MISSING_A", "MISSING_B"}


class TestValidateEnvTypes:
    def test_valid_int(self):
        result = validate_env(SAMPLE_ENV, {"PORT": "int"})
        assert result.type_mismatches == {}

    def test_invalid_int(self):
        env = {"PORT": "not_a_number"}
        result = validate_env(env, {"PORT": "int"})
        assert "PORT" in result.type_mismatches

    def test_valid_bool(self):
        result = validate_env(SAMPLE_ENV, {"DEBUG": "bool"})
        assert result.type_mismatches == {}

    def test_invalid_bool(self):
        env = {"DEBUG": "maybe"}
        result = validate_env(env, {"DEBUG": "bool"})
        assert "DEBUG" in result.type_mismatches

    def test_valid_float(self):
        result = validate_env(SAMPLE_ENV, {"RATIO": "float"})
        assert result.type_mismatches == {}

    def test_invalid_float(self):
        env = {"RATIO": "abc"}
        result = validate_env(env, {"RATIO": "float"})
        assert "RATIO" in result.type_mismatches

    def test_none_type_skips_type_check(self):
        env = {"PORT": "not_a_number"}
        result = validate_env(env, {"PORT": None})
        assert result.type_mismatches == {}

    def test_unknown_schema_type_raises(self):
        with pytest.raises(ValueError, match="Unknown schema type"):
            validate_env(SAMPLE_ENV, {"PORT": "uuid"})


class TestValidateEnvStrict:
    def test_strict_flags_unknown_keys(self):
        schema = {"APP_NAME": "str"}
        result = validate_env(SAMPLE_ENV, schema, strict=True)
        assert "PORT" in result.unknown_keys
        assert "DEBUG" in result.unknown_keys

    def test_non_strict_ignores_unknown_keys(self):
        schema = {"APP_NAME": "str"}
        result = validate_env(SAMPLE_ENV, schema, strict=False)
        assert result.unknown_keys == []

    def test_strict_valid_when_exact_match(self):
        schema = {k: None for k in SAMPLE_ENV}
        result = validate_env(SAMPLE_ENV, schema, strict=True)
        assert result.is_valid
