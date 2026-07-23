"""
YCONN – 07/2026 Duplikate bereinigen
======================================
Löscht für 07/2026 alle 'offen'-Einträge eines Kunden,
wenn für denselben Kunden bereits ein 'erstellt'-Eintrag existiert.

Ausführen:
    cd C:\\WF\\sap-robots
    python cleanup_july_duplicates.py
"""
import sqlite3
from pathlib import Path

DB = Path(r"Z:\DB\orchestrator.db")
PERIODE = "07/2026"

if not DB.exists():
    print(f"FEHLER: DB nicht erreichbar: {DB}")
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row

# Alle 07/2026-Einträge anzeigen
rows = conn.execute(
    "SELECT id, bukrs, kunden_nr, name, status, invoice_nr, order_nr "
    "FROM invoice_records WHERE periode=? ORDER BY kunden_nr, status",
    (PERIODE,)
).fetchall()

print(f"\n=== Alle {PERIODE}-Einträge ({len(rows)} Stück) ===")
for r in rows:
    print(f"  ID={r['id']:4d} | {r['bukrs']} | {r['kunden_nr']} | {r['status']:10s} "
          f"| Faktura={r['invoice_nr'] or '–':12s} | Auftrag={r['order_nr'] or '–'}")

# Kunden mit 'erstellt'-Eintrag ermitteln
erstellt = conn.execute(
    "SELECT DISTINCT kunden_nr FROM invoice_records WHERE periode=? AND status='erstellt'",
    (PERIODE,)
).fetchall()
erstellt_kunden = {r['kunden_nr'] for r in erstellt}

print(f"\nKunden mit 'erstellt' in {PERIODE}: {sorted(erstellt_kunden)}")

# 'offen'-Einträge für diese Kunden finden
to_delete = conn.execute(
    "SELECT id, kunden_nr, name, order_nr FROM invoice_records "
    "WHERE periode=? AND status='offen' AND kunden_nr IN ({})".format(
        ','.join('?' * len(erstellt_kunden))
    ),
    (PERIODE,) + tuple(sorted(erstellt_kunden))
).fetchall()

if not to_delete:
    print("\nKeine Duplikate gefunden – nichts zu tun.")
    conn.close()
    raise SystemExit(0)

print(f"\nZu löschende 'offen'-Duplikate ({len(to_delete)} Stück):")
for r in to_delete:
    print(f"  ID={r['id']:4d} | Kunde={r['kunden_nr']} | {r['name']} | Auftrag={r['order_nr'] or '–'}")

confirm = input("\nJetzt löschen? (ja/nein): ").strip().lower()
if confirm != 'ja':
    print("Abgebrochen.")
    conn.close()
    raise SystemExit(0)

ids = [r['id'] for r in to_delete]
conn.execute(
    "DELETE FROM invoice_records WHERE id IN ({})".format(','.join('?' * len(ids))),
    ids
)
conn.commit()
conn.close()

print(f"\n✅ {len(ids)} Duplikate gelöscht. Bitte Seite neu laden (Strg+F5).")
