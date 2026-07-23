"""
DB-Migration: Z:\\DB\\orchestrator.db → C:\\WF\\sap-robots\\orchestrator\\orchestrator.db
Dieses Skript direkt auf dem Windows-Rechner ausführen (BEVOR der Orchestrator neu startet).
"""
import sqlite3
import shutil
import json
import sys
from pathlib import Path
from datetime import datetime

SOURCE = Path(r"Z:\DB\orchestrator.db")
TARGET = Path(r"C:\WF\sap-robots\orchestrator\orchestrator.db")
CONFIG = Path(r"C:\WF\sap-robots\orchestrator\db_config.json")

def migrate():
    print("=" * 60)
    print("  YCONN – DB-Migration nach Lokal")
    print("=" * 60)

    # Quelle prüfen
    if not SOURCE.exists():
        print(f"\n  FEHLER: Quelldatei nicht gefunden: {SOURCE}")
        print("  Ist das Z:-Laufwerk verbunden?")
        sys.exit(1)

    src_size = SOURCE.stat().st_size / (1024 * 1024)
    print(f"\n  Quelle : {SOURCE}  ({src_size:.1f} MB)")
    print(f"  Ziel   : {TARGET}")
    print()

    # Zielverzeichnis sicherstellen
    TARGET.parent.mkdir(parents=True, exist_ok=True)

    # SQLite backup API (sicherer als einfaches Kopieren)
    print("  Kopiere Datenbank (SQLite Backup API)...")
    src_con = sqlite3.connect(str(SOURCE), timeout=10)
    dst_con = sqlite3.connect(str(TARGET), timeout=10)
    src_con.backup(dst_con, pages=200)
    src_con.close()
    dst_con.close()

    dst_size = TARGET.stat().st_size / (1024 * 1024)
    print(f"  ✅ Kopiert: {dst_size:.1f} MB")

    # Tabellen und Datensätze zählen
    con = sqlite3.connect(str(TARGET))
    tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    total_rows = 0
    for (t,) in tables:
        try:
            cnt = con.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
            total_rows += cnt
        except Exception:
            pass
    con.close()
    print(f"  Tabellen : {len(tables)}")
    print(f"  Datensätze: {total_rows}")

    # db_config.json aktualisieren
    cfg = {
        "db_path":       str(TARGET),
        "db_dir":        str(TARGET.parent),
        "previous_path": str(SOURCE),
        "updated_at":    datetime.now().isoformat(),
        "updated_by":    "db_migrate_lokal.py"
    }
    CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  ✅ db_config.json aktualisiert → {TARGET}")

    print()
    print("=" * 60)
    print("  Migration abgeschlossen!")
    print("  → Orchestrator jetzt neu starten.")
    print("=" * 60)
    print()

if __name__ == "__main__":
    migrate()
    input("  Enter drücken zum Schließen...")
