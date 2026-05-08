"""Scores an env file for quality based on common best-practice heuristics."""

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.profiler import _is_sensitive

# Penalty weights
_PENALTY_EMPTY_VALUE = 5
_PENALTY_SENSITIVE_PLAIN = 20
_PENALTY_LONG_LINE = 3
_PENALTY_NO_COMMENT_BLOCK = 2
_MAX_RECOMMENDED_LINE_LEN = 120


@dataclass
class ScoreIssue:
    key: str
    message: str
    penalty: int


@dataclass
class ScoreResult:
    total_keys: int
    score: int  # 0-100
    issues: List[ScoreIssue] = field(default_factory=list)

    @property
    def grade(self) -> str:
        if self.score >= 90:
            return "A"
        if self.score >= 75:
            return "B"
        if self.score >= 60:
            return "C"
        if self.score >= 40:
            return "D"
        return "F"


def score_env(env: Dict[str, str], raw_lines: List[str] = None) -> ScoreResult:
    """Compute a quality score (0-100) for the given env mapping.

    Args:
        env: Parsed key/value mapping.
        raw_lines: Optional original lines from the file for line-length checks.

    Returns:
        A ScoreResult with score, grade, and individual issues.
    """
    issues: List[ScoreIssue] = []
    total_penalty = 0

    for key, value in env.items():
        # Penalise empty values
        if value == "":
            issue = ScoreIssue(key, "Empty value", _PENALTY_EMPTY_VALUE)
            issues.append(issue)
            total_penalty += issue.penalty

        # Penalise sensitive keys that look like they hold a real (plain) value
        if _is_sensitive(key) and value not in ("", "<secret>", "CHANGE_ME", "TODO"):
            issue = ScoreIssue(
                key,
                "Sensitive key may contain a plain-text secret",
                _PENALTY_SENSITIVE_PLAIN,
            )
            issues.append(issue)
            total_penalty += issue.penalty

    # Penalise overly long lines
    if raw_lines:
        for lineno, line in enumerate(raw_lines, start=1):
            stripped = line.rstrip("\n")
            if len(stripped) > _MAX_RECOMMENDED_LINE_LEN:
                key_part = stripped.split("=")[0].lstrip("export ").strip()
                issue = ScoreIssue(
                    key_part or f"line:{lineno}",
                    f"Line {lineno} exceeds {_MAX_RECOMMENDED_LINE_LEN} characters",
                    _PENALTY_LONG_LINE,
                )
                issues.append(issue)
                total_penalty += issue.penalty

    score = max(0, 100 - total_penalty)
    return ScoreResult(total_keys=len(env), score=score, issues=issues)
