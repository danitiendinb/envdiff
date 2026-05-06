"""Tests for envdiff.importer module."""

import pytest

from envdiff.importer import (
    import_from_json,
    import_from_yaml,
    import_from_shell,
    import_env,
)


class TestImportFromJson:
    def test_simple_string_values(self):
        result = import_from_json('{"KEY": "value", "PORT": "8080"}')
        assert result == {"KEY": "value", "PORT": "8080"}

    def test_numeric_values_coerced_to_string(self):
        result = import_from_json('{"PORT": 8080}')
        assert result["PORT"] == "8080"

    def test_empty_object(self):
        assert import_from_json("{}") == {}

    def test_non_dict_raises(self):
        with pytest.raises(ValueError, match="root must be"):
            import_from_json('["a", "b"]')

    def test_invalid_json_raises(self):
        with pytest.raises(Exception):
            import_from_json("not json")


class TestImportFromYaml:
    def test_plain_value(self):
        result = import_from_yaml("KEY: value")
        assert result == {"KEY": "value"}

    def test_quoted_value(self):
        result = import_from_yaml('URL: "http://example.com"')
        assert result["URL"] == "http://example.com"

    def test_empty_quoted_value(self):
        result = import_from_yaml('EMPTY: ""')
        assert result["EMPTY"] == ""

    def test_comments_ignored(self):
        src = "# comment\nKEY: val\n"
        result = import_from_yaml(src)
        assert "KEY" in result
        assert len(result) == 1

    def test_blank_lines_ignored(self):
        result = import_from_yaml("\nKEY: val\n\n")
        assert result == {"KEY": "val"}

    def test_multiple_entries(self):
        src = "A: 1\nB: 2\n"
        result = import_from_yaml(src)
        assert result == {"A": "1", "B": "2"}


class TestImportFromShell:
    def test_single_quoted_export(self):
        result = import_from_shell("export FOO='bar'")
        assert result["FOO"] == "bar"

    def test_double_quoted_export(self):
        result = import_from_shell('export FOO="bar"')
        assert result["FOO"] == "bar"

    def test_unquoted_value(self):
        result = import_from_shell("export FOO=bar")
        assert result["FOO"] == "bar"

    def test_without_export_keyword(self):
        result = import_from_shell("FOO='baz'")
        assert result["FOO"] == "baz"

    def test_multiple_exports(self):
        src = "export A='1'\nexport B='2'\n"
        result = import_from_shell(src)
        assert result == {"A": "1", "B": "2"}

    def test_shebang_line_ignored(self):
        src = "#!/bin/sh\nexport KEY='val'\n"
        result = import_from_shell(src)
        assert list(result.keys()) == ["KEY"]


class TestImportEnv:
    def test_json_dispatch(self):
        result = import_env('{"X": "1"}', fmt="json")
        assert result == {"X": "1"}

    def test_yaml_dispatch(self):
        result = import_env("X: 1", fmt="yaml")
        assert result == {"X": "1"}

    def test_shell_dispatch(self):
        result = import_env("export X='1'", fmt="shell")
        assert result == {"X": "1"}

    def test_case_insensitive_format(self):
        result = import_env('{"X": "1"}', fmt="JSON")
        assert result == {"X": "1"}

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError, match="Unsupported import format"):
            import_env("data", fmt="toml")
