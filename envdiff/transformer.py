"""Transform env dicts by applying key/value mutations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)

    @property
    def changed_keys(self) -> List[str]:
        return [
            k for k in self.transformed
            if self.transformed[k] != self.original.get(k)
        ]

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_keys)


def _uppercase_keys(env: Dict[str, str]) -> Dict[str, str]:
    return {k.upper(): v for k, v in env.items()}


def _strip_value_whitespace(env: Dict[str, str]) -> Dict[str, str]:
    return {k: v.strip() for k, v in env.items()}


def _prefix_keys(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    return {f"{prefix}{k}": v for k, v in env.items()}


def _remove_prefix_from_keys(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    result = {}
    for k, v in env.items():
        if k.startswith(prefix):
            result[k[len(prefix):]] = v
        else:
            result[k] = v
    return result


def _mask_sensitive_values(
    env: Dict[str, str],
    sensitive_fragments: Optional[List[str]] = None,
    mask: str = "***",
) -> Dict[str, str]:
    fragments = sensitive_fragments or ["password", "secret", "token", "api_key"]
    result = {}
    for k, v in env.items():
        lower_k = k.lower()
        if any(f in lower_k for f in fragments):
            result[k] = mask
        else:
            result[k] = v
    return result


def transform_env(
    env: Dict[str, str],
    uppercase_keys: bool = False,
    strip_whitespace: bool = False,
    add_prefix: Optional[str] = None,
    remove_prefix: Optional[str] = None,
    mask_sensitive: bool = False,
    sensitive_fragments: Optional[List[str]] = None,
    mask_value: str = "***",
) -> TransformResult:
    """Apply a chain of transformations to an env dict."""
    result = dict(env)
    applied: List[str] = []

    if strip_whitespace:
        result = _strip_value_whitespace(result)
        applied.append("strip_whitespace")

    if uppercase_keys:
        result = _uppercase_keys(result)
        applied.append("uppercase_keys")

    if remove_prefix:
        result = _remove_prefix_from_keys(result, remove_prefix)
        applied.append(f"remove_prefix:{remove_prefix}")

    if add_prefix:
        result = _prefix_keys(result, add_prefix)
        applied.append(f"add_prefix:{add_prefix}")

    if mask_sensitive:
        result = _mask_sensitive_values(result, sensitive_fragments, mask_value)
        applied.append("mask_sensitive")

    return TransformResult(original=dict(env), transformed=result, applied=applied)
