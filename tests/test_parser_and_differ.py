"""Tests for the .env parser and differ modules."""

import pytest

from envdiff.parser import parse_env_string
from envdiff.differ import diff_envs, EnvDiffResult


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

class TestParseEnvString:
    def test_simple_key_value(self):
        result = parse_env_string("FOO=bar")
        assert result == {"FOO": "bar"}

    def test_double_quoted_value(self):
        result = parse_env_string('DB_URL="postgres://localhost/mydb"')
        assert result["DB_URL"] == "postgres://localhost/mydb"

    def test_single_quoted_value(self):
        result = parse_env_string("SECRET='my secret'")
        assert result["SECRET"] == "my secret"

    def test_export_prefix(self):
        result = parse_env_string("export API_KEY=abc123")
        assert result["API_KEY"] == "abc123"

    def test_comments_and_blanks_ignored(self):
        content = "\n# This is a comment\nFOO=1\n\nBAR=2\n"
        result = parse_env_string(content)
        assert result == {"FOO": "1", "BAR": "2"}

    def test_empty_value(self):
        result = parse_env_string("EMPTY=")
        assert result["EMPTY"] == ""

    def test_malformed_line_raises(self):
        with pytest.raises(ValueError, match="Malformed .env line 1"):
            parse_env_string("THIS IS NOT VALID")

    def test_multiple_variables(self):
        content = "HOST=localhost\nPORT=5432\nDEBUG=false"
        result = parse_env_string(content)
        assert result == {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


# ---------------------------------------------------------------------------
# Differ tests
# ---------------------------------------------------------------------------

class TestDiffEnvs:
    BASE = {"A": "1", "B": "2", "C": "3"}
    TARGET = {"A": "1", "B": "99", "D": "4"}

    def test_added_keys(self):
        result = diff_envs(self.BASE, self.TARGET)
        assert result.added == {"D": "4"}

    def test_removed_keys(self):
        result = diff_envs(self.BASE, self.TARGET)
        assert result.removed == {"C": "3"}

    def test_changed_keys(self):
        result = diff_envs(self.BASE, self.TARGET)
        assert result.changed == {"B": ("2", "99")}

    def test_unchanged_keys(self):
        result = diff_envs(self.BASE, self.TARGET)
        assert "A" in result.unchanged

    def test_has_differences_true(self):
        result = diff_envs(self.BASE, self.TARGET)
        assert result.has_differences is True

    def test_has_differences_false(self):
        result = diff_envs(self.BASE, self.BASE)
        assert result.has_differences is False

    def test_identical_envs(self):
        result = diff_envs(self.BASE, self.BASE)
        assert result.added == {}
        assert result.removed == {}
        assert result.changed == {}
        assert sorted(result.unchanged) == sorted(self.BASE.keys())

    def test_empty_envs(self):
        result = diff_envs({}, {})
        assert not result.has_differences
