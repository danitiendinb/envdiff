"""Tests for envdiff.grouper and envdiff.group_reporter."""
from __future__ import annotations

import pytest

from envdiff.grouper import (
    GroupResult,
    _extract_prefix,
    group_by_prefix,
    group_by_rules,
)
from envdiff.group_reporter import format_group_report


# ---------------------------------------------------------------------------
# _extract_prefix
# ---------------------------------------------------------------------------

def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_without_underscore():
    assert _extract_prefix("PORT") is None


def test_extract_prefix_multiple_underscores():
    assert _extract_prefix("AWS_S3_BUCKET") == "AWS"


def test_extract_prefix_custom_delimiter():
    assert _extract_prefix("db.host", delimiter=".") == "db"


# ---------------------------------------------------------------------------
# group_by_prefix
# ---------------------------------------------------------------------------

def test_group_by_prefix_basic():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "PORT": "8080"}
    result = group_by_prefix(env)
    assert "DB" in result.groups
    assert result.groups["DB"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert "PORT" in result.ungrouped


def test_group_by_prefix_min_group_size_filters_small_groups():
    env = {"DB_HOST": "localhost", "AWS_KEY": "abc", "AWS_SECRET": "xyz"}
    result = group_by_prefix(env, min_group_size=2)
    assert "AWS" in result.groups
    assert "DB" not in result.groups
    assert "DB_HOST" in result.ungrouped


def test_group_by_prefix_empty_env():
    result = group_by_prefix({})
    assert result.groups == {}
    assert result.ungrouped == {}


def test_group_names_sorted():
    env = {"Z_KEY": "1", "A_KEY": "2", "A_OTHER": "3"}
    result = group_by_prefix(env)
    assert result.group_names() == ["A", "Z"]


def test_total_groups():
    env = {"DB_HOST": "h", "DB_PORT": "p", "REDIS_URL": "r", "REDIS_TTL": "t"}
    result = group_by_prefix(env)
    assert result.total_groups() == 2


# ---------------------------------------------------------------------------
# group_by_rules
# ---------------------------------------------------------------------------

def test_group_by_rules_basic():
    env = {"DB_HOST": "localhost", "PORT": "8080", "SECRET": "s"}
    rules = {"database": ["DB_HOST"], "app": ["PORT"]}
    result = group_by_rules(env, rules)
    assert result.groups["database"] == {"DB_HOST": "localhost"}
    assert result.groups["app"] == {"PORT": "8080"}
    assert "SECRET" in result.ungrouped


def test_group_by_rules_missing_key_ignored():
    env = {"A": "1"}
    rules = {"grp": ["A", "MISSING"]}
    result = group_by_rules(env, rules)
    assert result.groups["grp"] == {"A": "1"}


def test_group_by_rules_empty_rules():
    env = {"A": "1", "B": "2"}
    result = group_by_rules(env, {})
    assert result.groups == {}
    assert result.ungrouped == {"A": "1", "B": "2"}


# ---------------------------------------------------------------------------
# format_group_report
# ---------------------------------------------------------------------------

def test_format_report_contains_group_name():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = group_by_prefix(env)
    report = format_group_report(result, use_color=False)
    assert "[DB]" in report


def test_format_report_shows_ungrouped():
    env = {"PORT": "8080"}
    result = group_by_prefix(env)
    report = format_group_report(result, use_color=False)
    assert "[ungrouped]" in report


def test_format_report_empty_env():
    result = GroupResult(groups={}, ungrouped={})
    report = format_group_report(result, use_color=False)
    assert "(no keys)" in report


def test_format_report_summary_line():
    env = {"DB_HOST": "h", "DB_PORT": "p", "LONE": "x"}
    result = group_by_prefix(env)
    report = format_group_report(result, use_color=False)
    assert "1 group(s)" in report
    assert "1 ungrouped key(s)" in report
