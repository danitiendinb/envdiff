"""Type-casting utilities for .env values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


@dataclass
class CastResult:
    original: Dict[str, str]
    casted: Dict[str, Any]
    skipped: List[str] = field(default_factory=list)

    @property
    def cast_count(self) -> int:
        return sum(1 for k in self.casted if self.casted[k] != self.original.get(k))

    @property
    def has_skipped(self) -> bool:
        return bool(self.skipped)


def _cast_value(value: str) -> Any:
    """Attempt to cast a string value to int, float, bool, or leave as str."""
    if value.lower() in _TRUE_VALUES:
        return True
    if value.lower() in _FALSE_VALUES:
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def cast_env(
    env: Dict[str, str],
    keys: List[str] | None = None,
    skip_keys: List[str] | None = None,
) -> CastResult:
    """Cast env values to native Python types.

    Args:
        env: Parsed environment dict (all string values).
        keys: If provided, only cast these keys.
        skip_keys: Keys to leave as raw strings.

    Returns:
        CastResult with original and casted dicts.
    """
    skip_set = set(skip_keys or [])
    target_keys = set(keys) if keys else set(env.keys())
    target_keys -= skip_set

    casted: Dict[str, Any] = dict(env)
    skipped: List[str] = list(skip_set & set(env.keys()))

    for k in target_keys:
        if k in env:
            casted[k] = _cast_value(env[k])

    return CastResult(original=dict(env), casted=casted, skipped=skipped)
