"""
YCONN – Symmetrische Verschlüsselung für SAP-Verbindungsdaten
=============================================================
Algorithmus : Fernet (AES-128-CBC + HMAC-SHA256)
Schlüssel   : secret.key  (im Projektstamm, NICHT in Git!)
Präfix      : ENC:         kennzeichnet verschlüsselte Werte

Verwendung
----------
>>> from crypto import encrypt, decrypt
>>> enc = encrypt("Catensys.22")    # => "ENC:gAAAAAB..."
>>> decrypt(enc)                    # => "Catensys.22"
>>> decrypt("Catensys.22")          # => "Catensys.22"  (kein Prefix → unverändert)
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger("yconn.crypto")

# Schlüsseldatei immer im Projektstamm (ein Verzeichnis über dieser Datei)
_KEY_PATH: Path = Path(__file__).parent / "secret.key"
_PREFIX   : str  = "ENC:"
_fernet   : Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is not None:
        return _fernet

    if not _KEY_PATH.exists():
        key = Fernet.generate_key()
        _KEY_PATH.write_bytes(key)
        try:
            os.chmod(_KEY_PATH, 0o600)          # nur Owner lesen/schreiben
        except Exception:
            pass                                # Windows ignoriert das — kein Problem
        log.info("Neuer Verschlüsselungsschlüssel erzeugt: %s", _KEY_PATH)
    else:
        key = _KEY_PATH.read_bytes()

    _fernet = Fernet(key)
    return _fernet


def encrypt(plaintext: str) -> str:
    """Verschlüsselt *plaintext* und gibt 'ENC:<token>' zurück.
    Bereits verschlüsselte Strings (ENC:-Präfix) werden unverändert durchgereicht.
    Leere Strings werden nicht verschlüsselt."""
    if not plaintext or plaintext.startswith(_PREFIX):
        return plaintext
    token = _get_fernet().encrypt(plaintext.encode("utf-8")).decode("ascii")
    return _PREFIX + token


def decrypt(value: str) -> str:
    """Entschlüsselt einen ENC:-String.  Werte ohne Präfix werden unverändert zurückgegeben."""
    if not value or not value.startswith(_PREFIX):
        return value
    try:
        return _get_fernet().decrypt(value[len(_PREFIX):].encode("ascii")).decode("utf-8")
    except InvalidToken:
        raise ValueError(
            "Entschlüsselung fehlgeschlagen – falscher Schlüssel oder korrupter Wert."
        )


def is_encrypted(value: str) -> bool:
    """Gibt True zurück wenn *value* mit ENC: beginnt."""
    return bool(value and value.startswith(_PREFIX))
