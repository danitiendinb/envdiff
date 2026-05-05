"""Serialize a key/value dict back to a .env-formatted string."""

from typing import Dict, Iterable, Optional

_NEEDS_QUOTING_CHARS = set(' \t#$\\"\'')


def _should_quote(value: str) -> bool:
    """Return True if *value* contains characters that require quoting."""
    if not value:
        return True
    return any(ch in _NEEDS_QUOTING_CHARS for ch in value)


def _quote_value(value: str) -> str:
    """Wrap *value* in double quotes, escaping internal double quotes."""
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def serialize_env(
    env: Dict[str, str],
    key_order: Optional[Iterable[str]] = None,
    add_export: bool = False,
) -> str:
    """Serialize *env* to a .env-formatted string.

    Parameters
    ----------
    env:
        Mapping of variable names to values.
    key_order:
        Optional iterable of keys that controls output order.  Keys present
        in *env* but absent from *key_order* are appended at the end in
        insertion order.
    add_export:
        When ``True`` each line is prefixed with ``export ``.
    """
    ordered_keys: list[str] = []
    if key_order is not None:
        for k in key_order:
            if k in env:
                ordered_keys.append(k)
    remaining = [k for k in env if k not in ordered_keys]
    all_keys = ordered_keys + remaining

    lines = []
    prefix = "export " if add_export else ""
    for key in all_keys:
        value = env[key]
        formatted_value = _quote_value(value) if _should_quote(value) else value
        lines.append(f"{prefix}{key}={formatted_value}")

    return "\n".join(lines) + ("\n" if lines else "")
