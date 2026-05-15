"""Variable interpolation for .env files.

Expands ${VAR} and $VAR references within values using a provided
environment mapping, with support for default fallbacks via ${VAR:-default}.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(
    r"\$\{(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?::-(?P<default>[^}]*))?\}"
    r"|\$(?P<bare>[A-Za-z_][A-Za-z0-9_]*)"
)


@dataclass
class InterpolateResult:
    env: Dict[str, str]
    expanded: Dict[str, str]  # keys whose values changed
    unresolved: List[str]     # keys that had references with no value found


def expanded_keys(result: InterpolateResult) -> List[str]:
    return list(result.expanded.keys())


def has_unresolved(result: InterpolateResult) -> bool:
    return bool(result.unresolved)


def _expand_value(value: str, env: Dict[str, str]) -> tuple[str, bool, bool]:
    """Return (expanded_value, was_changed, had_unresolved)."""
    unresolved = False

    def replacer(m: re.Match) -> str:
        nonlocal unresolved
        name = m.group("name") or m.group("bare")
        default: Optional[str] = m.group("default") if m.group("name") else None
        if name in env:
            return env[name]
        if default is not None:
            return default
        unresolved = True
        return m.group(0)  # leave original token intact

    expanded = _REF_RE.sub(replacer, value)
    return expanded, expanded != value, unresolved


def interpolate_env(
    env: Dict[str, str],
    context: Optional[Dict[str, str]] = None,
) -> InterpolateResult:
    """Expand variable references in *env* values.

    Args:
        env: The environment dict to interpolate.
        context: Extra variables available for expansion (defaults to *env*
                 itself, allowing self-referential expansion in definition order).
    """
    lookup: Dict[str, str] = {}
    if context:
        lookup.update(context)

    result: Dict[str, str] = {}
    expanded: Dict[str, str] = {}
    unresolved: List[str] = []

    for key, value in env.items():
        new_value, changed, had_unresolved = _expand_value(value, lookup)
        result[key] = new_value
        # Make the resolved value available to subsequent keys
        lookup[key] = new_value
        if changed:
            expanded[key] = new_value
        if had_unresolved:
            unresolved.append(key)

    return InterpolateResult(env=result, expanded=expanded, unresolved=unresolved)
