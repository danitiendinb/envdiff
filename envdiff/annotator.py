"""Annotate .env keys with inline comments describing their purpose or metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AnnotateResult:
    """Result of annotating an env mapping."""
    annotated: Dict[str, str] = field(default_factory=dict)
    comments: Dict[str, str] = field(default_factory=dict)

    @property
    def annotation_count(self) -> int:
        return len(self.comments)

    @property
    def has_annotations(self) -> bool:
        return bool(self.comments)

    def render_line(self, key: str) -> str:
        """Render a key=value line with optional trailing comment."""
        value = self.annotated.get(key, "")
        comment = self.comments.get(key)
        line = f"{key}={value}"
        if comment:
            line = f"{line}  # {comment}"
        return line


def annotate_env(
    env: Dict[str, str],
    rules: Dict[str, str],
    *,
    annotate_sensitive: bool = True,
) -> AnnotateResult:
    """Attach comments to keys that match annotation rules.

    Args:
        env: Mapping of key -> value.
        rules: Mapping of key substring (case-insensitive) -> comment text.
        annotate_sensitive: When True, add a generic "sensitive" comment to
            keys that look like secrets but have no explicit rule match.

    Returns:
        AnnotateResult with the original env preserved and comments populated.
    """
    _SENSITIVE_FRAGMENTS = ("password", "secret", "token", "apikey", "api_key", "private")

    comments: Dict[str, str] = {}

    for key in env:
        key_lower = key.lower()
        matched: Optional[str] = None

        for fragment, comment in rules.items():
            if fragment.lower() in key_lower:
                matched = comment
                break

        if matched is None and annotate_sensitive:
            for frag in _SENSITIVE_FRAGMENTS:
                if frag in key_lower:
                    matched = "sensitive — do not commit"
                    break

        if matched is not None:
            comments[key] = matched

    return AnnotateResult(annotated=dict(env), comments=comments)


def render_annotated(result: AnnotateResult) -> str:
    """Render the full annotated env as a .env-formatted string."""
    lines = [result.render_line(key) for key in result.annotated]
    return "\n".join(lines)
