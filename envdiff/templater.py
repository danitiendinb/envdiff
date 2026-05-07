"""Generate .env template files from existing env dicts or files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.auditor import _is_sensitive_key  # reuse sensitive detection


@dataclass
class TemplateEntry:
    key: str
    default: str
    comment: Optional[str] = None
    required: bool = True


@dataclass
class EnvTemplate:
    entries: List[TemplateEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, str]:
        return {e.key: e.default for e in self.entries}


def _make_comment(key: str, has_value: bool) -> str:
    parts = []
    if _is_sensitive_key(key):
        parts.append("sensitive")
    if not has_value:
        parts.append("required")
    return ", ".join(parts) if parts else ""


def build_template(
    env: Dict[str, str],
    redact_sensitive: bool = True,
    placeholder: str = "",
) -> EnvTemplate:
    """Build an EnvTemplate from a populated env dict."""
    entries: List[TemplateEntry] = []
    for key, value in sorted(env.items()):
        is_sensitive = _is_sensitive_key(key)
        default = placeholder if (redact_sensitive and is_sensitive) else value
        comment = _make_comment(key, bool(value))
        entries.append(
            TemplateEntry(
                key=key,
                default=default,
                comment=comment or None,
                required=not bool(value),
            )
        )
    return EnvTemplate(entries=entries)


def render_template(template: EnvTemplate) -> str:
    """Render an EnvTemplate to a .env-style string."""
    lines: List[str] = []
    for entry in template.entries:
        if entry.comment:
            lines.append(f"# {entry.comment}")
        lines.append(f"{entry.key}={entry.default}")
    return "\n".join(lines) + "\n" if lines else ""


def template_from_keys(
    keys: List[str],
    placeholder: str = "",
) -> EnvTemplate:
    """Build a blank template from a list of key names."""
    entries = [
        TemplateEntry(
            key=k,
            default=placeholder,
            comment=_make_comment(k, False) or None,
            required=True,
        )
        for k in sorted(keys)
    ]
    return EnvTemplate(entries=entries)
