"""
Migration: invoice_email_configs + invoice_email_history anlegen
Ausführen: python migrate_email_tables.py
"""
import sqlite3, os, pathlib

DB = pathlib.Path(__file__).parent / "orchestrator.db"
if not DB.exists():
    print(f"FEHLER: DB nicht gefunden: {DB}")
    raise SystemExit(1)

con = sqlite3.connect(str(DB))
cur = con.cursor()
existing = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
print("Vorhandene Tabellen:", sorted(existing))

TABLES = {
    "invoice_email_configs": """
        CREATE TABLE invoice_email_configs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            kunden_nr        TEXT    UNIQUE NOT NULL,
            name             TEXT    DEFAULT '',
            recipient_email  TEXT    NOT NULL,
            sender_email     TEXT    NOT NULL,
            smtp_host        TEXT    DEFAULT '',
            smtp_port        INTEGER DEFAULT 587,
            smtp_user        TEXT    DEFAULT '',
            smtp_pass        TEXT    DEFAULT '',
            smtp_tls         INTEGER DEFAULT 1,
            subject_template TEXT    DEFAULT 'Rechnung {invoice_nr} - {name} - {periode}',
            body_template    TEXT    DEFAULT '',
            status           TEXT    DEFAULT 'aktiv',
            auto_send        INTEGER DEFAULT 0,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
    "invoice_email_history": """
        CREATE TABLE invoice_email_history (
            id                INTEGER  PRIMARY KEY AUTOINCREMENT,
            invoice_record_id INTEGER  DEFAULT 0,
            kunden_nr         TEXT     DEFAULT '',
            invoice_nr        TEXT     DEFAULT '',
            periode           TEXT     DEFAULT '',
            recipient_email   TEXT     NOT NULL,
            sender_email      TEXT     NOT NULL,
            subject           TEXT     DEFAULT '',
            status            TEXT     DEFAULT 'ausstehend',
            error_msg         TEXT     DEFAULT '',
            sent_at           DATETIME DEFAULT CURRENT_TIMESTAMP
        )""",
}

for tbl, ddl in TABLES.items():
    if tbl not in existing:
        cur.execute(ddl)
        print(f"  ✓ Tabelle '{tbl}' angelegt")
    else:
        print(f"  – Tabelle '{tbl}' bereits vorhanden")

con.commit()
con.close()
print("\nMigration abgeschlossen.")
