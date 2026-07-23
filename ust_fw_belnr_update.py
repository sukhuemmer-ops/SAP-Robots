"""
USt-Firmenwagen 06/2026 — Belegnummern aus SAP nachtragen
Liest den Lauf aus der DB, trägt die SAP-Dokumentnummern ein,
setzt Status = booked und speichert zurück.

Ausführen: python ust_fw_belnr_update.py
"""
import sqlite3, json, os, sys

# ── Konfiguration ────────────────────────────────────────────────────────────
DB_PATH = r"Z:\DB\orchestrator.db"

# Zuordnung: Nachname → SAP-Belegnummer (aus FB03 / Buchungsjournal)
BELNR_MAP = {
    "Thiam":       "2300013021",
    "Ullein":      "2300013022",
    "Sass":        "2300013023",
    "von Bauer":   "2300013024",
    "Grillmeier":  "2300013025",
    "Steininger":  "2300013026",
    "Bodenstein":  "2300013027",
    "Fellmann":    "2300013028",
    "Janik":       "2300013029",
    "Pagel":       "2300013030",
}

# ── DB laden ─────────────────────────────────────────────────────────────────
if not os.path.exists(DB_PATH):
    print(f"FEHLER: DB nicht gefunden: {DB_PATH}")
    sys.exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Lauf für 06/2026 suchen
runs = conn.execute("""
    SELECT id, periode, fis_period, fisc_year, lines_json, status
    FROM ust_firmenwagen_runs
    WHERE (fis_period IN ('6','06') AND fisc_year='2026')
       OR periode LIKE '06/2026%'
    ORDER BY id DESC
""").fetchall()

if not runs:
    print("Kein Lauf für 06/2026 gefunden.")
    conn.close()
    sys.exit(1)

print(f"Gefundene Läufe für 06/2026:")
for i, r in enumerate(runs):
    lines = json.loads(r['lines_json'] or '[]')
    booked = sum(1 for l in lines if l.get('status') == 'booked')
    print(f"  [{i}] Run #{r['id']} — Periode: {r['periode']} — {len(lines)} Zeilen — {booked} gebucht — Status: {r['status']}")

# Bei mehreren Läufen: neuesten nehmen
run = runs[0]
print(f"\nVerarbeite Run #{run['id']} ...")

lines = json.loads(run['lines_json'] or '[]')

# ── Belegnummern zuordnen ────────────────────────────────────────────────────
updated = 0
not_found = []

for line in lines:
    nachname = line.get('nachname', '')
    # Exakte Übereinstimmung versuchen
    belnr = BELNR_MAP.get(nachname)
    # Fallback: Teilstring-Suche
    if not belnr:
        for name_key, doc_nr in BELNR_MAP.items():
            if name_key.lower() in nachname.lower() or nachname.lower() in name_key.lower():
                belnr = doc_nr
                break
    if belnr:
        line['belnr']  = belnr
        line['status'] = 'booked'
        updated += 1
        print(f"  ✅ {nachname:20s} → {belnr}")
    else:
        not_found.append(nachname)
        print(f"  ❓ {nachname:20s} → NICHT zugeordnet")

if not_found:
    print(f"\n⚠  {len(not_found)} Zeile(n) ohne Zuordnung: {', '.join(not_found)}")

# Gesamtstatus berechnen
all_booked  = all(l.get('status') == 'booked' for l in lines)
any_booked  = any(l.get('status') == 'booked' for l in lines)
run_status  = 'booked' if all_booked else ('partial' if any_booked else 'saved')

new_json = json.dumps(lines, ensure_ascii=False)

# ── In DB schreiben ──────────────────────────────────────────────────────────
conn.execute("""
    UPDATE ust_firmenwagen_runs
    SET lines_json = ?, status = ?
    WHERE id = ?
""", (new_json, run_status, run['id']))
conn.commit()
conn.close()

print(f"\n✅ Run #{run['id']} aktualisiert:")
print(f"   {updated}/{len(lines)} Zeilen mit Belegnr. versehen")
print(f"   Gesamtstatus: {run_status}")
print(f"\nDie Belegnummern sind jetzt in der Cockpit-Ansicht sichtbar.")
print("→ Verlauf-Tab öffnen → Lauf #{} laden".format(run['id']))
