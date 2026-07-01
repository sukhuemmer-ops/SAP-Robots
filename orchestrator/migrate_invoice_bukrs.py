"""Migration: bukrs-Spalte zu invoice_records hinzufügen."""
import sqlite3, os, glob, pathlib

BASE = pathlib.Path(__file__).parent

def migrate(db_path):
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()
    cur.execute("PRAGMA table_info(invoice_records)")
    cols = [r[1] for r in cur.fetchall()]
    if not cols:
        print(f"  Tabelle invoice_records nicht vorhanden in {db_path} – übersprungen")
        conn.close()
        return
    if "bukrs" not in cols:
        cur.execute('ALTER TABLE invoice_records ADD COLUMN bukrs TEXT DEFAULT "0435"')
        conn.commit()
        print(f"  ✓ bukrs-Spalte hinzugefügt in {os.path.basename(db_path)}")
    else:
        print(f"  ✓ bukrs bereits vorhanden in {os.path.basename(db_path)}")
    conn.close()

if __name__ == "__main__":
    dbs = list(BASE.glob("*.db"))
    if not dbs:
        print("Keine DB-Dateien gefunden.")
    for db in dbs:
        print(f"Migriere {db.name}…")
        migrate(str(db))
    print("Fertig.")
