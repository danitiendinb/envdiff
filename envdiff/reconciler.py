"""Reconcile .env files by merging, filling missing keys, or generating patches."""

from typing import Dict, Optional
from envdiff.differ import EnvDiffResult, diff_envs


def reconcile_missing(
    base: Dict[str, str],
    target: Dict[str, str],
    fill_value: str = "",
) -> Dict[str, str]:
    """Return a copy of *target* with keys missing from base added.

    Keys present in *base* but absent from *target* are injected using
    *fill_value* as a placeholder so the target env is never missing a key
    that the base declares.
    """
    result = dict(target)
    diff: EnvDiffResult = diff_envs(base, target)
    for key in diff.only_in_base:
        result[key] = fill_value
    return result


def reconcile_overrides(
    base: Dict[str, str],
    overrides: Dict[str, str],
) -> Dict[str, str]:
    """Merge *overrides* on top of *base*, returning a new dict.

    Values present in *overrides* win; keys only in *base* are kept;
    keys only in *overrides* are appended.
    """
    merged = dict(base)
    merged.update(overrides)
    return merged


def generate_patch(
    base: Dict[str, str],
    target: Dict[str, str],
) -> Dict[str, Optional[str]]:
    """Return a minimal patch dict to transform *base* into *target*.

    The patch maps each changed or added key to its new value in *target*,
    and maps each key removed from *base* to ``None``.
    """
    diff: EnvDiffResult = diff_envs(base, target)
    patch: Dict[str, Optional[str]] = {}

    for key in diff.only_in_target:
        patch[key] = target[key]

    for key in diff.only_in_base:
        patch[key] = None  # signals deletion

    for key, (base_val, target_val) in diff.changed.items():
        patch[key] = target_val

    return patch


def apply_patch(
    base: Dict[str, str],
    patch: Dict[str, Optional[str]],
) -> Dict[str, str]:
    """Apply a *patch* produced by :func:`generate_patch` to *base*."""
    result = dict(base)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = value
    return result
