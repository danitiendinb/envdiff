"""Tests for envdiff.serializer."""

import pytest
from envdiff.serializer import serialize_env, _should_quote, _quote_value


class TestShouldQuote:
    def test_plain_value_no_quote(self):
        assert _should_quote("simple") is False

    def test_value_with_space_needs_quote(self):
        assert _should_quote("hello world") is True

    def test_empty_string_needs_quote(self):
        assert _should_quote("") is True

    def test_value_with_hash_needs_quote(self):
        assert _should_quote("val#ue") is True


class TestQuoteValue:
    def test_wraps_in_double_quotes(self):
        assert _quote_value("hello world") == '"hello world"'

    def test_escapes_internal_double_quotes(self):
        assert _quote_value('say "hi"') == '"say \\"hi\\""'

    def test_escapes_backslash(self):
        assert _quote_value("path\\to") == '"path\\\\to"'


class TestSerializeEnv:
    def test_basic_serialization(self):
        env = {"HOST": "localhost", "PORT": "5432"}
        output = serialize_env(env)
        assert "HOST=localhost" in output
        assert "PORT=5432" in output

    def test_values_with_spaces_are_quoted(self):
        env = {"GREETING": "hello world"}
        output = serialize_env(env)
        assert 'GREETING="hello world"' in output

    def test_empty_value_is_quoted(self):
        env = {"EMPTY": ""}
        output = serialize_env(env)
        assert 'EMPTY=""' in output

    def test_export_prefix(self):
        env = {"KEY": "value"}
        output = serialize_env(env, add_export=True)
        assert output.startswith("export KEY=value")

    def test_key_order_respected(self):
        env = {"B": "2", "A": "1", "C": "3"}
        output = serialize_env(env, key_order=["C", "A", "B"])
        lines = output.strip().splitlines()
        assert lines[0].startswith("C=")
        assert lines[1].startswith("A=")
        assert lines[2].startswith("B=")

    def test_trailing_newline(self):
        env = {"X": "1"}
        assert serialize_env(env).endswith("\n")

    def test_empty_env_no_newline(self):
        assert serialize_env({}) == ""
