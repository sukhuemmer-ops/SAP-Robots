"""
YCONN – Verschlüsselung zurücksetzen
=====================================
Löscht secret.key, fragt nach den Klartextpasswörtern
und verschlüsselt alles neu.

Ausführen:
    cd C:\\WF\\sap-robots
    python reset_encryption.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent
KEY_FILE = ROOT / "secret.key"

# 1. secret.key löschen damit ein neuer generiert wird
if KEY_FILE.exists():
    KEY_FILE.unlink()
    print(f"✓  {KEY_FILE} gelöscht")
else:
    print(f"–  {KEY_FILE} war nicht vorhanden")

# 2. crypto neu laden (generiert automatisch neuen Key)
sys.path.insert(0, str(ROOT))
from crypto import encrypt, _KEY_PATH  # noqa

print(f"✓  Neuer Schlüssel generiert: {_KEY_PATH}")

# 3. Passwörter abfragen
print()
print("Bitte Klartextpasswörter eingeben (werden NICHT angezeigt):")
import getpass
sap_pw     = getpass.getpass("  SAP_PASSWORD       : ")
sap_db_pw  = getpass.getpass("  SAP_DB_PASSWORD    : ")

if not sap_pw or not sap_db_pw:
    print("FEHLER: Passwörter dürfen nicht leer sein. Abbruch.")
    sys.exit(1)

# 4. Verschlüsseln
enc_sap    = encrypt(sap_pw)
enc_sap_db = encrypt(sap_db_pw)
print()
print(f"SAP_PASSWORD    = {enc_sap}")
print(f"SAP_DB_PASSWORD = {enc_sap_db}")

# 5. Alle .env-Dateien aktualisieren
import re
ENV_FILES = [
    ROOT / "worker" / ".env",
    ROOT / "worker" / ".env.dev",
    ROOT / "worker" / ".env.test",
    ROOT / "worker" / ".env.prod",
]

PATTERN = re.compile(r'^(SAP_PASSWORD|SAP_DB_PASSWORD)=.*$', re.MULTILINE)

MAP = {"SAP_PASSWORD": enc_sap, "SAP_DB_PASSWORD": enc_sap_db}

for env_file in ENV_FILES:
    if not env_file.exists():
        continue
    text = env_file.read_text(encoding="utf-8")
    new_text = PATTERN.sub(lambda m: f"{m.group(1)}={MAP[m.group(1)]}", text)
    if new_text != text:
        env_file.write_text(new_text, encoding="utf-8")
        print(f"  ✓  {env_file.relative_to(ROOT)} aktualisiert")
    else:
        print(f"  –  {env_file.relative_to(ROOT)}: kein SAP_PASSWORD / SAP_DB_PASSWORD Eintrag")

print()
print("✅  Fertig! Bitte Bridge und Orchestrator neu starten.")
print(f"⚠   Sichern Sie {_KEY_PATH} auf einem USB-Stick!")
