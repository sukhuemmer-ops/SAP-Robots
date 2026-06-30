"""
Direkte Datenbank-Verbindung zur SAP Sybase ASE.
================================================
Wird verwendet, wenn KEIN SAP NW RFC SDK installiert ist und stattdessen
direkt auf die DB-Tabellen (BSID, BSAD, KNA1, KNB1, ...) zugegriffen wird.

Voraussetzungen
---------------
* Installiertes SAP ASE Client SDK (du hast: SDKASE160004P_5-21012005)
* ODBC-Treiber 'Adaptive Server Enterprise' (kommt mit dem SDK)
* pip install pyodbc
* DB-User mit Lese-Rechten auf die SAP-Schemata

Umgebungsvariablen
------------------
SAP_DB_DRIVER       Treibername in odbcad32, default 'Adaptive Server Enterprise'
SAP_DB_HOST         ASE-Server-IP/Hostname (oft gleich SAP_ASHOST, hier: 172.28.189.8)
SAP_DB_PORT         ASE-Port, default 5000
SAP_DB_NAME         Datenbank-Name (z. B. PRD, P01, oder die SAP-SID)
SAP_DB_USER         DB-User (NICHT der RFC-User! Eigener DB-Login wie 'sapsa' oder 'rpa_read')
SAP_DB_PASSWORD_REF Vault-Referenz, default env://SAP_DB_PASSWORD
SAP_DB_CHARSET      Default 'utf8'

Wichtige Hinweise
-----------------
* SAP-Tabellen in ASE haben IMMER eine MANDT-Spalte (Mandant). Jede Abfrage muss
  WHERE MANDT = ? mitfiltern, sonst bekommst du Daten aus allen Mandanten.
* Du umgehst die SAP-Berechtigung. Der DB-User sieht alles, was er sehen darf.
* Nur lesend einsetzen! Schreibende Aktionen ueber DB sind in SAP tabu.
"""
from __future__ import annotations

import logging
import os

from sap_secrets import resolve_secret_cached

log = logging.getLogger("sap_db")


def build_ase_connection_string() -> str:
    """Baut den ODBC-Connection-String aus Umgebungsvariablen."""
    driver = os.getenv("SAP_DB_DRIVER", "Adaptive Server Enterprise")
    host   = os.getenv("SAP_DB_HOST")   or os.getenv("SAP_ASHOST")
    port   = os.getenv("SAP_DB_PORT", "5000")
    dbname = os.getenv("SAP_DB_NAME")
    user   = os.getenv("SAP_DB_USER")
    pw_ref = os.getenv("SAP_DB_PASSWORD_REF", "env://SAP_DB_PASSWORD")
    charset = os.getenv("SAP_DB_CHARSET", "utf8")

    missing = []
    if not host:   missing.append("SAP_DB_HOST")
    if not dbname: missing.append("SAP_DB_NAME")
    if not user:   missing.append("SAP_DB_USER")
    if missing:
        raise RuntimeError(
            "DB-Verbindungs-Variablen fehlen: " + ", ".join(missing) +
            ". Bitte .env ergaenzen."
        )

    password = resolve_secret_cached(pw_ref)
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={host};"
        f"PORT={port};"
        f"DB={dbname};"
        f"UID={user};"
        f"PWD={password};"
        f"CHARSET={charset};"
    )


def get_connection():
    """Oeffnet eine pyodbc-Verbindung zur SAP ASE. Aufrufer muss .close() machen."""
    import pyodbc  # type: ignore  # pip install pyodbc
    cs = build_ase_connection_string()
    # Connection-String ohne Passwort fuers Log
    safe_cs = "; ".join(p for p in cs.split(";") if not p.startswith("PWD="))
    log.info("ASE-Verbindung: %s", safe_cs)
    return pyodbc.connect(cs, autocommit=True)


def ping() -> str:
    """Diagnose: einfache SELECT-Abfrage gegen ASE."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT @@version")
        row = cur.fetchone()
        version = row[0] if row else "(unbekannt)"
        cur.execute("SELECT db_name()")
        dbname = cur.fetchone()[0]
        cur.execute("SELECT @@servername")
        server = cur.fetchone()[0]
        return f"ASE OK: Server={server}, DB={dbname}, Version={str(version)[:60]}..."
    finally:
        conn.close()


def list_drivers() -> list:
    """Listet alle installierten ODBC-Treiber. Hilfreich, wenn 'driver not found'."""
    try:
        import pyodbc
        return list(pyodbc.drivers())
    except ImportError:
        return []
