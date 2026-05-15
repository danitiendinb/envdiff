"""Tests for envdiff.annotator and envdiff.annotate_reporter."""
from __future__ import annotations

import io
import pytest

from envdiff.annotator import AnnotateResult, annotate_env, render_annotated
from envdiff.annotate_reporter import format_annotate_report, print_annotate_report


def _env(**kwargs: str) -> dict[str, str]:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# AnnotateResult helpers
# ---------------------------------------------------------------------------

class TestAnnotateResult:
    def test_annotation_count(self):
        r = AnnotateResult(annotated={"A": "1", "B": "2"}, comments={"A": "note"})
        assert r.annotation_count == 1

    def test_has_annotations_true(self):
        r = AnnotateResult(annotated={"A": "1"}, comments={"A": "x"})
        assert r.has_annotations is True

    def test_has_annotations_false(self):
        r = AnnotateResult(annotated={"A": "1"}, comments={})
        assert r.has_annotations is False

    def test_render_line_with_comment(self):
        r = AnnotateResult(annotated={"DB_URL": "postgres://"}, comments={"DB_URL": "connection"})
        assert r.render_line("DB_URL") == "DB_URL=postgres://  # connection"

    def test_render_line_without_comment(self):
        r = AnnotateResult(annotated={"PORT": "8080"}, comments={})
        assert r.render_line("PORT") == "PORT=8080"


# ---------------------------------------------------------------------------
# annotate_env
# ---------------------------------------------------------------------------

class TestAnnotateEnv:
    def test_explicit_rule_matched(self):
        env = _env(DB_HOST="localhost")
        result = annotate_env(env, rules={"DB": "database setting"})
        assert "DB_HOST" in result.comments
        assert result.comments["DB_HOST"] == "database setting"

    def test_rule_match_is_case_insensitive(self):
        env = _env(db_host="localhost")
        result = annotate_env(env, rules={"DB": "database setting"})
        assert "db_host" in result.comments

    def test_no_rule_no_sensitive_no_annotation(self):
        env = _env(PORT="8080")
        result = annotate_env(env, rules={})
        assert result.comments == {}

    def test_sensitive_key_auto_annotated(self):
        env = _env(DB_PASSWORD="s3cr3t")
        result = annotate_env(env, rules={})
        assert "DB_PASSWORD" in result.comments
        assert "sensitive" in result.comments["DB_PASSWORD"]

    def test_sensitive_annotation_disabled(self):
        env = _env(API_TOKEN="abc")
        result = annotate_env(env, rules={}, annotate_sensitive=False)
        assert result.comments == {}

    def test_original_env_preserved(self):
        env = _env(FOO="bar", BAZ="qux")
        result = annotate_env(env, rules={})
        assert result.annotated == env

    def test_explicit_rule_takes_precedence_over_sensitive(self):
        env = _env(API_SECRET="x")
        result = annotate_env(env, rules={"API_SECRET": "custom note"})
        assert result.comments["API_SECRET"] == "custom note"


# ---------------------------------------------------------------------------
# render_annotated
# ---------------------------------------------------------------------------

def test_render_annotated_includes_comments():
    env = _env(PORT="8080", DB_PASSWORD="s3cr3t")
    result = annotate_env(env, rules={})
    rendered = render_annotated(result)
    assert "DB_PASSWORD=s3cr3t" in rendered
    assert "# sensitive" in rendered


def test_render_annotated_plain_key_no_comment():
    env = _env(PORT="8080")
    result = annotate_env(env, rules={}, annotate_sensitive=False)
    assert render_annotated(result) == "PORT=8080"


# ---------------------------------------------------------------------------
# format_annotate_report / print_annotate_report
# ---------------------------------------------------------------------------

class TestFormatAnnotateReport:
    def test_header_present(self):
        result = annotate_env(_env(PORT="8080"), rules={})
        report = format_annotate_report(result)
        assert "Annotation Report" in report

    def test_no_annotations_message(self):
        result = annotate_env(_env(PORT="8080"), rules={}, annotate_sensitive=False)
        report = format_annotate_report(result)
        assert "No annotations applied" in report

    def test_annotated_key_listed(self):
        result = annotate_env(_env(DB_PASSWORD="x"), rules={})
        report = format_annotate_report(result)
        assert "DB_PASSWORD" in report

    def test_counts_shown(self):
        env = _env(PORT="8080", DB_PASSWORD="x")
        result = annotate_env(env, rules={})
        report = format_annotate_report(result)
        assert "Total keys   : 2" in report
        assert "Annotated    : 1" in report

    def test_print_annotate_report_writes_to_stream(self):
        result = annotate_env(_env(PORT="8080"), rules={}, annotate_sensitive=False)
        buf = io.StringIO()
        print_annotate_report(result, file=buf)
        assert "Annotation Report" in buf.getvalue()
