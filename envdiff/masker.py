"""Mask sensitive values in an env mapping for safe display or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_FRAGMENTS = (
    "password", "passwd", "secret", "token", "api_key",
    "apikey", "auth", "credential", "private", "access_key",
)

_DEFAULT_MASK = "***"
_DEFAULT_VISIBLE_CHARS = 0


def is_sensitive_key(key: str) -> bool:
    """Return True if *key* looks like it holds a sensitive value."""
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


@dataclass
class MaskResult:
    """Result of masking an env mapping."""
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def mask_count(self) -> int:
        return len(self.masked_keys)

    @property
    def has_masked(self) -> bool:
        return self.mask_count > 0


def _apply_mask(value: str, mask: str, visible_chars: int) -> str:
    """Return a masked representation of *value*."""
    if not value:
        return mask
    if visible_chars > 0 and len(value) > visible_chars:
        return value[:visible_chars] + mask
    return mask


def mask_env(
    env: Dict[str, str],
    *,
    mask: str = _DEFAULT_MASK,
    visible_chars: int = _DEFAULT_VISIBLE_CHARS,
    extra_keys: List[str] | None = None,
) -> MaskResult:
    """Return a *MaskResult* where sensitive values are replaced with *mask*.

    Args:
        env: The source env mapping.
        mask: The replacement string for sensitive values.
        visible_chars: How many leading characters to keep before the mask.
        extra_keys: Additional key names to treat as sensitive.
    """
    sensitive_extras = {k.lower() for k in (extra_keys or [])}
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        if is_sensitive_key(key) or key.lower() in sensitive_extras:
            masked[key] = _apply_mask(value, mask, visible_chars)
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(original=dict(env), masked=masked, masked_keys=sorted(masked_keys))
