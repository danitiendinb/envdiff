"""Tests for envdiff.caster and envdiff.cast_reporter."""
from __future__ import annotations

import pytest

from envdiff.caster import CastResult, _cast_value, cast_env
from envdiff.cast_reporter import format_cast_report


# ---------------------------------------------------------------------------
# _cast_value unit tests
# ---------------------------------------------------------------------------

class TestCastValue:
    def test_integer_string(self):
        assert _cast_value("42") == 42
        assert isinstance(_cast_value("42"), int)

    def test_float_string(self):
        assert _cast_value("3.14") == pytest.approx(3.14)
        assert isinstance(_cast_value("3.14"), float)

    def test_true_variants(self):
        for v in ("true", "True", "TRUE", "1", "yes", "on"):
            assert _cast_value(v) is True

    def test_false_variants(self):
        for v in ("false", "False", "FALSE", "0", "no", "off"):
            assert _cast_value(v) is False

    def test_plain_string_unchanged(self):
        assert _cast_value("hello") == "hello"
        assert isinstance(_cast_value("hello"), str)

    def test_empty_string_unchanged(self):
        assert _cast_value("") == ""


# ---------------------------------------------------------------------------
# cast_env tests
# ---------------------------------------------------------------------------

class TestCastEnv:
    def _env(self):
        return {
            "PORT": "8080",
            "DEBUG": "true",
            "RATIO": "0.75",
            "NAME": "myapp",
            "SECRET_KEY": "abc123",
        }

    def test_all_keys_cast_by_default(self):
        result = cast_env(self._env())
        assert result.casted["PORT"] == 8080
        assert result.casted["DEBUG"] is True
        assert result.casted["RATIO"] == pytest.approx(0.75)
        assert result.casted["NAME"] == "myapp"

    def test_cast_count_reflects_changes(self):
        result = cast_env(self._env())
        # PORT, DEBUG, RATIO change; NAME and SECRET_KEY stay str
        assert result.cast_count == 3

    def test_skip_keys_leaves_value_as_string(self):
        result = cast_env(self._env(), skip_keys=["PORT"])
        assert result.casted["PORT"] == "8080"
        assert isinstance(result.casted["PORT"], str)
        assert "PORT" in result.skipped

    def test_has_skipped_true_when_skipped(self):
        result = cast_env(self._env(), skip_keys=["DEBUG"])
        assert result.has_skipped is True

    def test_has_skipped_false_when_none_skipped(self):
        result = cast_env(self._env())
        assert result.has_skipped is False

    def test_keys_filter_limits_casting(self):
        result = cast_env(self._env(), keys=["PORT"])
        assert result.casted["PORT"] == 8080
        # DEBUG not in keys list so stays as original string
        assert result.casted["DEBUG"] == "true"

    def test_original_dict_is_unchanged(self):
        env = self._env()
        result = cast_env(env)
        assert result.original == env

    def test_empty_env(self):
        result = cast_env({})
        assert result.casted == {}
        assert result.cast_count == 0


# ---------------------------------------------------------------------------
# cast_reporter tests
# ---------------------------------------------------------------------------

class TestFormatCastReport:
    def _result(self, **kwargs):
        env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
        return cast_env(env, **kwargs)

    def test_header_present(self):
        report = format_cast_report(self._result(), color=False)
        assert "Cast Report" in report

    def test_total_keys_shown(self):
        report = format_cast_report(self._result(), color=False)
        assert "Total keys" in report
        assert "3" in report

    def test_type_changes_listed(self):
        report = format_cast_report(self._result(), color=False)
        assert "PORT" in report
        assert "DEBUG" in report

    def test_no_changes_message_when_all_strings(self):
        result = cast_env({"NAME": "app", "ENV": "prod"})
        report = format_cast_report(result, color=False)
        assert "No type changes" in report

    def test_skipped_section_shown(self):
        result = cast_env({"PORT": "8080", "NAME": "app"}, skip_keys=["PORT"])
        report = format_cast_report(result, color=False)
        assert "Skipped" in report
        assert "PORT" in report
