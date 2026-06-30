"""
Diagnose-Skript fuer die direkte ASE-Verbindung.
================================================
Prueft Schritt fuer Schritt, ob die SQL-Verbindung zum SAP-Datenbank-Server steht.

Voraussetzung: pyodbc + ODBC-Treiber 'Adaptive Server Enterprise'.
"""
from __future__ import annotations

import sys
from pathlib import Path


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print("  " + title)
    print("=" * 70)


def ok(msg: str)   -> None: print(f"  [OK]    {msg}")
def fail(msg: str) -> int:  print(f"  [FEHLER] {msg}"); return 1


# --- Phase 1: .env laden ---
section("Phase 1: Umgebung laden")
try:
    from dotenv import load_dotenv
    here = Path(__file__).resolve().parent
    for c in (here / ".env", here / ".env.example"):
        if c.exists():
            load_dotenv(c); ok(f"Geladen: {c.name}"); break
except ImportError:
    print("  [WARN] python-dotenv fehlt (pip install python-dotenv)")

import os
required = ["SAP_DB_HOST", "SAP_DB_NAME", "SAP_DB_USER"]
missing = [v for v in required if not os.getenv(v)]
if missing:
    print(f"  [FEHLER] DB-Variablen fehlen: {missing}")
    print("           Bitte .env ergaenzen, siehe README oder Antwort von Claude.")
    sys.exit(1)
ok("DB-Variablen gesetzt: " + ", ".join(required))


# --- Phase 2: pyodbc + Treiber ---
section("Phase 2: pyodbc & ODBC-Treiber")
try:
    import pyodbc
    ok(f"pyodbc importiert (Version {pyodbc.version})")
except ImportError as exc:
    sys.exit(fail(f"pyodbc fehlt: {exc} - 'pip install pyodbc'"))

drivers = list(pyodbc.drivers())
print(f"  Installierte ODBC-Treiber:")
for d in drivers:
    print(f"    - {d}")
wanted = os.getenv("SAP_DB_DRIVER", "Adaptive Server Enterprise")
if any(wanted.lower() in d.lower() for d in drivers):
    ok(f"Treiber '{wanted}' verfuegbar")
else:
    print(f"  [WARN] Treiber '{wanted}' nicht gefunden in obiger Liste.")
    print(f"         Setze SAP_DB_DRIVER in .env auf einen der gelisteten Treibernamen,")
    print(f"         oder installiere den SAP ASE ODBC-Treiber (kommt mit dem ASE SDK).")


# --- Phase 3: Connection-String ---
section("Phase 3: Connection-String bauen")
try:
    from sap_db import build_ase_connection_string
    cs = build_ase_connection_string()
    safe = "; ".join(p for p in cs.split(";") if not p.startswith("PWD="))
    ok(safe)
except Exception as exc:  # noqa: BLE001
    sys.exit(fail(str(exc)))


# --- Phase 4: TCP zur DB ---
section("Phase 4: TCP-Verbindung")
import socket
host = os.getenv("SAP_DB_HOST")
port = int(os.getenv("SAP_DB_PORT", "5000"))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(5)
try:
    s.connect((host, port))
    ok(f"{host}:{port} erreichbar")
except Exception as exc:  # noqa: BLE001
    sys.exit(fail(f"{host}:{port} nicht erreichbar: {exc}"))
finally:
    s.close()


# --- Phase 5: SELECT @@version ---
section("Phase 5: Login + System-Info")
try:
    from sap_db import ping
    print("  " + ping())
    ok("ASE-Login erfolgreich")
except Exception as exc:  # noqa: BLE001
    sys.exit(fail(f"Login/Query fehlgeschlagen: {exc}"))


# --- Phase 6: Lese-Berechtigung auf SAP-Tabellen ---
section("Phase 6: SAP-Tabellen lesen (BSID, KNA1)")
try:
    from sap_db import get_connection
    conn = get_connection()
    cur = conn.cursor()
    mandt = os.getenv("SAP_CLIENT", "600")
    for tbl in ("BSID", "KNA1", "KNB1", "BKPF"):
        try:
            cur.execute(f"SELECT count(*) FROM {tbl} WHERE MANDT = ?", mandt)
            row = cur.fetchone()
            ok(f"{tbl:>6}: {row[0]} Zeilen (Mandant {mandt})")
        except Exception as exc:  # noqa: BLE001
            print(f"  [FEHLER] {tbl}: {exc}")
    conn.close()
except Exception as exc:  # noqa: BLE001
    sys.exit(fail(str(exc)))

print("\n" + "=" * 70)
print("  ASE-Test abgeschlossen.")
print("=" * 70)
