"""Tests for envdiff.scorer."""

import pytest

from envdiff.scorer import ScoreResult, ScoreIssue, score_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(**kwargs):
    return {k: v for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# TestScoreResult
# ---------------------------------------------------------------------------

class TestScoreResult:
    def test_grade_a(self):
        r = ScoreResult(total_keys=5, score=95)
        assert r.grade == "A"

    def test_grade_b(self):
        r = ScoreResult(total_keys=5, score=80)
        assert r.grade == "B"

    def test_grade_c(self):
        r = ScoreResult(total_keys=5, score=65)
        assert r.grade == "C"

    def test_grade_d(self):
        r = ScoreResult(total_keys=5, score=45)
        assert r.grade == "D"

    def test_grade_f(self):
        r = ScoreResult(total_keys=5, score=30)
        assert r.grade == "F"


# ---------------------------------------------------------------------------
# TestScoreEnv
# ---------------------------------------------------------------------------

class TestScoreEnv:
    def test_perfect_env_scores_100(self):
        env = _env(APP_NAME="myapp", DEBUG="false", PORT="8080")
        result = score_env(env)
        assert result.score == 100
        assert result.issues == []

    def test_empty_value_penalised(self):
        env = _env(APP_NAME="", PORT="8080")
        result = score_env(env)
        assert result.score < 100
        assert any(i.key == "APP_NAME" for i in result.issues)

    def test_sensitive_plain_value_penalised(self):
        env = _env(SECRET_KEY="supersecretvalue123")
        result = score_env(env)
        assert result.score < 100
        keys_with_issues = [i.key for i in result.issues]
        assert "SECRET_KEY" in keys_with_issues

    def test_sensitive_placeholder_not_penalised(self):
        env = _env(SECRET_KEY="CHANGE_ME")
        result = score_env(env)
        assert all(i.key != "SECRET_KEY" for i in result.issues)

    def test_sensitive_empty_not_double_penalised(self):
        """An empty sensitive key gets only the empty-value penalty, not the plain-secret penalty."""
        env = _env(API_TOKEN="")
        result = score_env(env)
        penalties = [i.penalty for i in result.issues if i.key == "API_TOKEN"]
        # Only the empty-value penalty should apply
        assert len(penalties) == 1

    def test_long_line_penalised(self):
        long_value = "x" * 130
        raw_lines = [f"SOME_KEY={long_value}\n"]
        env = {"SOME_KEY": long_value}
        result = score_env(env, raw_lines=raw_lines)
        assert result.score < 100
        assert any("SOME_KEY" in i.key or "line:1" in i.key for i in result.issues)

    def test_score_floor_is_zero(self):
        # Many issues should not push score below 0
        env = {f"SECRET_{i}": f"plainval{i}" for i in range(20)}
        result = score_env(env)
        assert result.score >= 0

    def test_total_keys_recorded(self):
        env = _env(A="1", B="2", C="3")
        result = score_env(env)
        assert result.total_keys == 3
