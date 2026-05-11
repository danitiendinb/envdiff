"""Encrypt and decrypt sensitive values in an env mapping."""

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "api_key", "apikey", "private")

_MARKER = "enc:"


def is_sensitive_key(key: str) -> bool:
    """Return True if *key* looks like it holds a sensitive value."""
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from *passphrase* using SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    """XOR *data* with *key* (repeated as needed)."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


@dataclass
class EncryptResult:
    original: Dict[str, str]
    encrypted: Dict[str, str]
    encrypted_keys: list = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.encrypted_keys)


def encrypt_env(
    env: Dict[str, str],
    passphrase: str,
    *,
    only_sensitive: bool = True,
    keys: Optional[list] = None,
) -> EncryptResult:
    """Return a new env dict with selected values encrypted.

    Values are encoded as ``enc:<base64>`` so they can be identified later.
    """
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    encrypted_keys: list = []

    for k, v in env.items():
        should_encrypt = (
            (keys is not None and k in keys)
            or (keys is None and only_sensitive and is_sensitive_key(k))
            or (keys is None and not only_sensitive)
        )
        if should_encrypt and not v.startswith(_MARKER):
            cipher = _xor_encrypt(v.encode(), key)
            result[k] = _MARKER + base64.b64encode(cipher).decode()
            encrypted_keys.append(k)
        else:
            result[k] = v

    return EncryptResult(original=env, encrypted=result, encrypted_keys=encrypted_keys)


def decrypt_env(env: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Return a new env dict with all ``enc:`` values decrypted."""
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    for k, v in env.items():
        if v.startswith(_MARKER):
            cipher = base64.b64decode(v[len(_MARKER):])
            result[k] = _xor_encrypt(cipher, key).decode()
        else:
            result[k] = v
    return result
