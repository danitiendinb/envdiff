"""Tests for envdiff.splitter and envdiff.split_reporter."""
import pytest

from envdiff.splitter import SplitResult, split_by_keys, split_by_prefix
from envdiff.split_reporter import format_split_report


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(**kwargs: str):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# split_by_prefix
# ---------------------------------------------------------------------------

class TestSplitByPrefix:
    def test_basic_partition(self):
        env = _env(DB_HOST="localhost", DB_PORT="5432", APP_NAME="myapp", OTHER="x")
        result = split_by_prefix(env, ["DB", "APP"])
        assert "DB_HOST" in result.partitions["DB"]
        assert "DB_PORT" in result.partitions["DB"]
        assert "APP_NAME" in result.partitions["APP"]
        assert result.unmatched == {"OTHER": "x"}

    def test_strip_prefix_removes_prefix_and_delimiter(self):
        env = _env(DB_HOST="localhost", DB_PORT="5432")
        result = split_by_prefix(env, ["DB"], strip_prefix=True)
        assert "HOST" in result.partitions["DB"]
        assert "PORT" in result.partitions["DB"]

    def test_case_insensitive_matching(self):
        env = {"db_host": "localhost"}
        result = split_by_prefix(env, ["DB"])
        assert "db_host" in result.partitions["DB"]

    def test_no_matching_prefix_all_unmatched(self):
        env = _env(FOO="1", BAR="2")
        result = split_by_prefix(env, ["DB"])
        assert result.unmatched == {"FOO": "1", "BAR": "2"}
        assert result.partitions["DB"] == {}

    def test_empty_env_returns_empty_partitions(self):
        result = split_by_prefix({}, ["DB", "APP"])
        assert result.total_keys() == 0
        assert not result.has_unmatched()

    def test_total_keys_counts_all(self):
        env = _env(DB_HOST="h", APP_NAME="n", EXTRA="e")
        result = split_by_prefix(env, ["DB", "APP"])
        assert result.total_keys() == 3

    def test_partition_names_returns_all_groups(self):
        result = split_by_prefix({}, ["A", "B", "C"])
        assert set(result.partition_names()) == {"A", "B", "C"}

    def test_first_matching_prefix_wins(self):
        """A key that matches multiple prefixes should go to the first one."""
        env = {"DB_EXTRA_HOST": "h"}
        result = split_by_prefix(env, ["DB", "DB_EXTRA"])
        assert "DB_EXTRA_HOST" in result.partitions["DB"]
        assert result.partitions["DB_EXTRA"] == {}


# ---------------------------------------------------------------------------
# split_by_keys
# ---------------------------------------------------------------------------

class TestSplitByKeys:
    def test_explicit_group_assignment(self):
        env = _env(HOST="h", PORT="p", SECRET="s")
        result = split_by_keys(env, {"network": ["HOST", "PORT"], "auth": ["SECRET"]})
        assert result.partitions["network"] == {"HOST": "h", "PORT": "p"}
        assert result.partitions["auth"] == {"SECRET": "s"}
        assert result.unmatched == {}

    def test_unlisted_key_goes_to_unmatched(self):
        env = _env(A="1", B="2")
        result = split_by_keys(env, {"g1": ["A"]})
        assert result.unmatched == {"B": "2"}

    def test_listed_key_absent_from_env_ignored(self):
        env = _env(A="1")
        result = split_by_keys(env, {"g1": ["A", "MISSING"]})
        assert "MISSING" not in result.partitions["g1"]

    def test_has_unmatched_false_when_all_assigned(self):
        env = _env(X="1")
        result = split_by_keys(env, {"g": ["X"]})
        assert not result.has_unmatched()


# ---------------------------------------------------------------------------
# format_split_report
# ---------------------------------------------------------------------------

class TestFormatSplitReport:
    def _result(self):
        env = _env(DB_HOST="localhost", DB_PORT="5432", APP_NAME="app", EXTRA="x")
        return split_by_prefix(env, ["DB", "APP"])

    def test_header_present(self):
        report = format_split_report(self._result(), color=False)
        assert "Env Split Report" in report

    def test_partition_names_in_report(self):
        report = format_split_report(self._result(), color=False)
        assert "[DB]" in report
        assert "[APP]" in report

    def test_unmatched_section_shown(self):
        report = format_split_report(self._result(), color=False)
        assert "unmatched" in report
        assert "EXTRA" in report

    def test_no_unmatched_message_when_all_matched(self):
        env = _env(DB_HOST="h")
        result = split_by_prefix(env, ["DB"])
        report = format_split_report(result, color=False)
        assert "All keys matched" in report
