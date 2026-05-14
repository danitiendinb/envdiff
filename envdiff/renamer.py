"""Rename keys across an env mapping with optional value preservation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameResult:
    env: Dict[str, str]
    renamed: List[tuple]          # list of (old_key, new_key)
    skipped: List[str]            # old keys that were absent in source
    overwritten: List[str]        # new keys that already existed and were replaced


def renamed_keys(result: RenameResult) -> List[tuple]:
    return result.renamed


def has_renames(result: RenameResult) -> bool:
    return bool(result.renamed)


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    drop_old: bool = True,
    overwrite: bool = True,
) -> RenameResult:
    """Rename keys in *env* according to *mapping* {old: new}.

    Parameters
    ----------
    env:       Source environment dict.
    mapping:   Dict mapping old key names to new key names.
    drop_old:  When True (default) the old key is removed after renaming.
    overwrite: When True (default) an existing key with the new name is
               replaced.  When False the rename is skipped if the new key
               already exists.
    """
    result_env: Dict[str, str] = dict(env)
    renamed: List[tuple] = []
    skipped: List[str] = []
    overwritten: List[str] = []

    for old_key, new_key in mapping.items():
        if old_key not in result_env:
            skipped.append(old_key)
            continue

        if new_key in result_env and not overwrite:
            skipped.append(old_key)
            continue

        if new_key in result_env and new_key != old_key:
            overwritten.append(new_key)

        value = result_env[old_key]
        if drop_old and new_key != old_key:
            del result_env[old_key]
        result_env[new_key] = value
        renamed.append((old_key, new_key))

    return RenameResult(
        env=result_env,
        renamed=renamed,
        skipped=skipped,
        overwritten=overwritten,
    )
