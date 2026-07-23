"""
YCONN – invoice_records Migration
===================================
Überträgt alle invoice_records aus der alten lokalen DB
in die neue Z:\\DB\\orchestrator.db (überspringt Duplikate).
Bereinigt dabei das Perioden-Format: 'YYYY/MM' → 'MM/YYYY'.

Ausführen:
    cd C:\\WF\\sap-robots
    python migrate_invoices.py
"""
import sqlite3
import re
from pathlib import Path

OLD_DB = Path(__file__).parent / "orchestrator" / "orchestrator.db"
NEW_DB = Path(r"Z:\DB\orchestrator.db")

def fix_periode(p: str) -> str:
    """'2026/07' → '07/2026', '07/2026' bleibt unverändert."""
    if p and re.match(r"^\d{4}/\d{2}$", p):
        year, month = p.split("/")
        return f"{month}/{year}"
    return p

print(f"Quelle : {OLD_DB}")
print(f"Ziel   : {NEW_DB}")

if not OLD_DB.exists():
    print("FEHLER: Alte DB nicht gefunden.")
    raise SystemExit(1)
if not NEW_DB.exists():
    print("FEHLER: Neue DB nicht erreichbar (Z: Laufwerk gemountet?).")
    raise SystemExit(1)

old = sqlite3.connect(str(OLD_DB))
new = sqlite3.connect(str(NEW_DB))
old.row_factory = sqlite3.Row

# Spalten der alten Tabelle
cols_raw = [r[1] for r in old.execute("PRAGMA table_info(invoice_records)").fetchall()]
# 'id' beim Insert weglassen (auto-increment in Ziel-DB)
cols = [c for c in cols_raw if c != "id"]

# Bestehende group_keys in neuer DB
existing = {r[0] for r in new.execute("SELECT group_key FROM invoice_records").fetchall()}
print(f"\nBereits in neuer DB: {len(existing)} Einträge")

rows = old.execute(f"SELECT {','.join(cols_raw)} FROM invoice_records").fetchall()
print(f"Einträge in alter DB: {len(rows)}")

inserted = 0
skipped  = 0
for row in rows:
    d = dict(row)
    d["periode"] = fix_periode(d.get("periode", "") or "")
    gk = d.get("group_key", "")
    if gk in existing:
        skipped += 1
        continue
    placeholders = ",".join(["?"] * len(cols))
    vals = [d[c] for c in cols]
    try:
        new.execute(
            f"INSERT INTO invoice_records ({','.join(cols)}) VALUES ({placeholders})",
            vals
        )
        existing.add(gk)
        inserted += 1
    except Exception as e:
        print(f"  WARN: {gk} → {e}")

# Bereinige auch falsche Formate in neuer DB
fixed = new.execute(
    "SELECT id, periode FROM invoice_records WHERE periode GLOB '????/??'"
).fetchall()
for rid, p in fixed:
    new.execute("UPDATE invoice_records SET periode=? WHERE id=?", (fix_periode(p), rid))
print(f"Perioden-Format-Fix in neuer DB: {len(fixed)} Einträge korrigiert")

new.commit()
old.close()
new.close()

print(f"\n✅  Fertig: {inserted} neue Einträge übertragen, {skipped} übersprungen.")
print("Bitte Orchestrator neu starten.")
