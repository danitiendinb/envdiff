"""Tests for envdiff.tagger and envdiff.tag_reporter."""

from __future__ import annotations

import io

import pytest

from envdiff.tagger import TagResult, tag_env
from envdiff.tag_reporter import format_tag_report, print_tag_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env() -> dict[str, str]:
    return {
        "DB_PASSWORD": "secret",
        "DB_HOST": "localhost",
        "API_TOKEN": "tok123",
        "APP_DEBUG": "true",
        "AWS_SECRET_KEY": "aws-secret",
    }


# ---------------------------------------------------------------------------
# TestTagEnv
# ---------------------------------------------------------------------------

class TestTagEnv:
    def test_returns_tag_result(self):
        result = tag_env(_env(), {})
        assert isinstance(result, TagResult)

    def test_no_rules_produces_empty_tags(self):
        result = tag_env(_env(), {})
        assert result.all_tags() == []
        for key in _env():
            assert result.tags_for_key(key) == frozenset()

    def test_single_rule_matches_substring(self):
        result = tag_env(_env(), {"database": ["DB_"]})
        assert set(result.keys_for_tag("database")) == {"DB_PASSWORD", "DB_HOST"}

    def test_tag_assigned_to_key(self):
        result = tag_env(_env(), {"secret": ["PASSWORD", "TOKEN", "SECRET"]})
        assert "secret" in result.tags_for_key("DB_PASSWORD")
        assert "secret" in result.tags_for_key("API_TOKEN")
        assert "secret" in result.tags_for_key("AWS_SECRET_KEY")
        assert "secret" not in result.tags_for_key("APP_DEBUG")

    def test_multiple_tags_on_same_key(self):
        result = tag_env(
            _env(),
            {"database": ["DB_"], "credentials": ["PASSWORD"]},
        )
        assert "database" in result.tags_for_key("DB_PASSWORD")
        assert "credentials" in result.tags_for_key("DB_PASSWORD")

    def test_case_insensitive_matching(self):
        result = tag_env({"db_host": "localhost"}, {"database": ["DB"]})
        assert "db_host" in result.keys_for_tag("database")

    def test_all_tags_sorted(self):
        result = tag_env(_env(), {"zebra": ["APP"], "alpha": ["DB_"]})
        assert result.all_tags() == ["alpha", "zebra"]

    def test_keys_for_missing_tag_returns_empty(self):
        result = tag_env(_env(), {})
        assert result.keys_for_tag("nonexistent") == []

    def test_env_preserved_unchanged(self):
        env = _env()
        result = tag_env(env, {"x": ["DB"]})
        assert result.env == env

    def test_tag_index_keys_are_sorted(self):
        result = tag_env(_env(), {"database": ["DB_"]})
        keys = result.keys_for_tag("database")
        assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# TestFormatTagReport
# ---------------------------------------------------------------------------

class TestFormatTagReport:
    def test_header_present(self):
        result = tag_env(_env(), {})
        report = format_tag_report(result, use_color=False)
        assert "Tag Report" in report

    def test_total_keys_shown(self):
        result = tag_env(_env(), {})
        report = format_tag_report(result, use_color=False)
        assert str(len(_env())) in report

    def test_no_tags_message(self):
        result = tag_env(_env(), {})
        report = format_tag_report(result, use_color=False)
        assert "No tags defined" in report

    def test_tag_label_in_report(self):
        result = tag_env(_env(), {"database": ["DB_"]})
        report = format_tag_report(result, use_color=False)
        assert "[database]" in report

    def test_matched_keys_listed(self):
        result = tag_env(_env(), {"database": ["DB_"]})
        report = format_tag_report(result, use_color=False)
        assert "DB_HOST" in report
        assert "DB_PASSWORD" in report

    def test_print_tag_report_writes_to_stream(self):
        result = tag_env(_env(), {"tok": ["TOKEN"]})
        buf = io.StringIO()
        print_tag_report(result, use_color=False, file=buf)
        assert "Tag Report" in buf.getvalue()
