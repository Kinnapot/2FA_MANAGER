from __future__ import annotations

import os
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken


_fernet: Optional[Fernet] = None


def ensure_key() -> None:
    key = os.getenv("FERNET_KEY")
    if not key:
        raise RuntimeError("FERNET_KEY is not set. Generate one and set in .env")


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        ensure_key()
        _fernet = Fernet(os.environ["FERNET_KEY"].encode())
    return _fernet


def encrypt(text: str) -> bytes:
    return _get_fernet().encrypt(text.encode())


def decrypt(blob: bytes) -> str:
    try:
        return _get_fernet().decrypt(blob).decode()
    except InvalidToken as e:
        raise ValueError("Invalid key or data") from e

