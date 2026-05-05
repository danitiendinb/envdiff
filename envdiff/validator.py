"""Validator module for checking .env files against a schema/template."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    """Result of validating an env dict against a schema."""
    missing_required: List[str] = field(default_factory=list)
    type_mismatches: Dict[str, str] = field(default_factory=dict)  # key -> expected type
    unknown_keys: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return (
            not self.missing_required
            and not self.type_mismatches
            and not self.unknown_keys
        )


SCHEMA_TYPES = {"str", "int", "float", "bool"}


def _check_type(value: str, expected: str) -> bool:
    """Return True if value can be interpreted as expected type."""
    if expected == "str":
        return True
    if expected == "int":
        try:
            int(value)
            return True
        except ValueError:
            return False
    if expected == "float":
        try:
            float(value)
            return True
        except ValueError:
            return False
    if expected == "bool":
        return value.lower() in {"true", "false", "1", "0", "yes", "no"}
    return True


def validate_env(
    env: Dict[str, str],
    schema: Dict[str, Optional[str]],
    strict: bool = False,
) -> ValidationResult:
    """Validate env dict against a schema.

    Args:
        env: Parsed environment variables.
        schema: Mapping of key -> expected type (or None for any type).
                Keys present in schema are considered required.
        strict: If True, keys in env not present in schema are flagged.

    Returns:
        A ValidationResult instance.
    """
    result = ValidationResult()
    schema_keys: Set[str] = set(schema.keys())
    env_keys: Set[str] = set(env.keys())

    # Check for missing required keys
    for key in schema_keys:
        if key not in env_keys:
            result.missing_required.append(key)

    # Check types for present keys
    for key, expected_type in schema.items():
        if key in env and expected_type is not None:
            if expected_type not in SCHEMA_TYPES:
                raise ValueError(f"Unknown schema type '{expected_type}' for key '{key}'")
            if not _check_type(env[key], expected_type):
                result.type_mismatches[key] = expected_type

    # Flag unknown keys in strict mode
    if strict:
        for key in env_keys:
            if key not in schema_keys:
                result.unknown_keys.append(key)

    return result
