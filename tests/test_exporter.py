"""Tests for envdiff.exporter module."""

import json
import pytest

from envdiff.exporter import (
    export_as_json,
    export_as_yaml,
    export_as_shell,
    export_env,
    SUPPORTED_FORMATS,
)


SAMPLE = {"DB_HOST": "localhost", "PORT": "5432", "SECRET": "abc123"}


class TestExportAsJson:
    def test_valid_json_output(self):
        result = export_as_json(SAMPLE)
        parsed = json.loads(result)
        assert parsed == SAMPLE

    def test_keys_are_sorted(self):
        result = export_as_json(SAMPLE)
        keys = list(json.loads(result).keys())
        assert keys == sorted(keys)

    def test_empty_env(self):
        assert export_as_json({}) == "{}"

    def test_custom_indent(self):
        result = export_as_json({"A": "1"}, indent=4)
        assert "    " in result


class TestExportAsYaml:
    def test_simple_values(self):
        result = export_as_yaml({"KEY": "value"})
        assert "KEY: value" in result

    def test_empty_value_is_quoted(self):
        result = export_as_yaml({"EMPTY": ""})
        assert 'EMPTY: ""' in result

    def test_value_with_colon_is_quoted(self):
        result = export_as_yaml({"URL": "http://example.com"})
        assert '"' in result

    def test_keys_are_sorted(self):
        result = export_as_yaml({"Z": "1", "A": "2"})
        lines = [l for l in result.splitlines() if l.strip()]
        assert lines[0].startswith("A:")
        assert lines[1].startswith("Z:")

    def test_empty_env(self):
        assert export_as_yaml({}) == "{}"


class TestExportAsShell:
    def test_starts_with_shebang(self):
        result = export_as_shell(SAMPLE)
        assert result.startswith("#!/bin/sh")

    def test_export_statements_present(self):
        result = export_as_shell({"FOO": "bar"})
        assert "export FOO='bar'" in result

    def test_single_quote_in_value_escaped(self):
        result = export_as_shell({"KEY": "it's"})
        assert "KEY=" in result
        assert "it" in result

    def test_empty_env_only_shebang(self):
        result = export_as_shell({})
        assert result == "#!/bin/sh"


class TestExportEnv:
    def test_json_format(self):
        result = export_env(SAMPLE, fmt="json")
        assert json.loads(result) == SAMPLE

    def test_yaml_format(self):
        result = export_env({"A": "1"}, fmt="yaml")
        assert "A: 1" in result

    def test_shell_format(self):
        result = export_env({"A": "1"}, fmt="shell")
        assert "export A='1'" in result

    def test_case_insensitive_format(self):
        result = export_env({"A": "1"}, fmt="JSON")
        assert json.loads(result) == {"A": "1"}

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_env(SAMPLE, fmt="toml")

    def test_supported_formats_constant(self):
        assert "json" in SUPPORTED_FORMATS
        assert "yaml" in SUPPORTED_FORMATS
        assert "shell" in SUPPORTED_FORMATS
