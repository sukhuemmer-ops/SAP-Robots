"""
YCONN – Einmaliges Verschlüsselungs-Setup
==========================================
Dieses Script liest die .env-Dateien von orchestrator/ und worker/,
verschlüsselt alle sensitiven SAP-Verbindungspasswörter (ENC:-Präfix)
und schreibt die Dateien zurück.

Einmalig ausführen:
    cd C:\\WF\\sap-robots
    python setup_encryption.py

Nach dem Ausführen:
  - secret.key liegt im Projektstamm  (NIE committen!)
  - SAP_PASSWORD=ENC:...  in allen .env-Dateien
  - Die App entschlüsselt automatisch beim Start

Felder die verschlüsselt werden
--------------------------------
  SAP_PASSWORD, SAP_DB_PASSWORD
  (Passwörter für SAP RFC-Service-Account und SAP-Datenbank-User)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# crypto.py liegt im gleichen Verzeichnis
sys.path.insert(0, str(Path(__file__).parent))
from crypto import encrypt, is_encrypted

# Welche .env-Keys sollen verschlüsselt werden?
SENSITIVE_KEYS = {"SAP_PASSWORD", "SAP_DB_PASSWORD"}

ENV_FILES = [
    Path("orchestrator/.env"),
    Path("orchestrator/.env.dev"),
    Path("orchestrator/.env.test"),
    Path("orchestrator/.env.prod"),
    Path("worker/.env"),
    Path("worker/.env.dev"),
    Path("worker/.env.test"),
    Path("worker/.env.prod"),
]

LINE_RE = re.compile(r'^([A-Z_][A-Z0-9_]*)=(.*)$')


def process_env_file(path: Path) -> None:
    if not path.exists():
        return

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = False
    new_lines = []

    for line in lines:
        m = LINE_RE.match(line.rstrip("\r\n"))
        if m:
            key, val = m.group(1), m.group(2)
            if key in SENSITIVE_KEYS and val and not is_encrypted(val):
                encrypted = encrypt(val)
                new_line = f"{key}={encrypted}\n"
                print(f"  ✓  {path}: {key} verschlüsselt")
                new_lines.append(new_line)
                changed = True
                continue
        new_lines.append(line if line.endswith("\n") else line + "\n")

    if changed:
        path.write_text("".join(new_lines), encoding="utf-8")
    else:
        print(f"  –  {path}: keine Änderungen (bereits verschlüsselt oder leer)")


def main() -> None:
    print("=" * 60)
    print("YCONN – SAP-Verbindungsdaten verschlüsseln")
    print("=" * 60)

    for env_file in ENV_FILES:
        process_env_file(env_file)

    key_path = Path("secret.key")
    if key_path.exists():
        print(f"\n✅  Schlüsseldatei: {key_path.resolve()}")
    print("\n⚠   Bitte sichern Sie secret.key separat (z. B. auf einem USB-Stick)!")
    print("    Ohne diesen Schlüssel sind die verschlüsselten Passwörter verloren.\n")


if __name__ == "__main__":
    main()
