"""
YCONN – App Backup
==================
Erstellt ein versioniertes ZIP-Archiv der gesamten App.

Verwendung:
    python backup.py              → Backup erstellen
    python backup.py --list       → Vorhandene Backups anzeigen
    python backup.py --restore X  → Backup Nr. X entpacken (Bestätigung erforderlich)

Speicherort: C:\WF\sap-robots\backups\
Format:      YCONN_Backup_v<NR>_<DATUM>_<UHRZEIT>.zip
"""

import argparse
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# ── Konfiguration ─────────────────────────────────────────────────────────────
APP_ROOT    = Path(__file__).parent.resolve()
BACKUP_DIR  = APP_ROOT / "backups"
VERSION_FILE = APP_ROOT / "backups" / "backup_version.json"

# Dateien/Ordner die NICHT ins Backup aufgenommen werden
EXCLUDE_DIRS = {
    "__pycache__", ".venv", "venv", ".git",
    "node_modules", "backups",          # Backups selbst nie einschließen
    "queue",                            # Worker-Queue (temporär)
}
EXCLUDE_FILES = {
    ".pyc", ".pyo", ".pyd",            # Compiled Python
    ".log",                             # Log-Dateien
    ".tmp", ".temp",
}
EXCLUDE_NAMES = {
    "desktop.ini", "thumbs.db", ".DS_Store",
}


# ── Versionsverwaltung ────────────────────────────────────────────────────────
def load_version() -> dict:
    BACKUP_DIR.mkdir(exist_ok=True)
    if VERSION_FILE.exists():
        try:
            return json.loads(VERSION_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": 0, "backups": []}


def save_version(data: dict) -> None:
    BACKUP_DIR.mkdir(exist_ok=True)
    VERSION_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ── Dateifilter ───────────────────────────────────────────────────────────────
def should_include(path: Path) -> bool:
    # Ordner prüfen
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return False
    # Dateinamen
    if path.name.lower() in EXCLUDE_NAMES:
        return False
    # Endungen
    if path.suffix.lower() in EXCLUDE_FILES:
        return False
    return True


# ── Backup erstellen ──────────────────────────────────────────────────────────
def create_backup(note: str = "") -> None:
    data    = load_version()
    ver_nr  = data["version"] + 1
    now     = datetime.now()
    ts      = now.strftime("%Y%m%d_%H%M%S")
    date_hr = now.strftime("%d.%m.%Y %H:%M")
    name    = f"YCONN_Backup_v{ver_nr:03d}_{ts}.zip"
    out     = BACKUP_DIR / name

    print(f"\n{'='*60}")
    print(f"  YCONN App Backup – Version {ver_nr:03d}")
    print(f"  {date_hr}")
    print(f"{'='*60}")
    print(f"  Quelle : {APP_ROOT}")
    print(f"  Ziel   : {out}")
    print()

    files_added = 0
    skipped     = 0

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for fpath in sorted(APP_ROOT.rglob("*")):
            if not fpath.is_file():
                continue
            rel = fpath.relative_to(APP_ROOT)
            if not should_include(rel):
                skipped += 1
                continue
            zf.write(fpath, rel)
            files_added += 1
            # Fortschritt alle 50 Dateien
            if files_added % 50 == 0:
                print(f"  ... {files_added} Dateien verarbeitet", end="\r")

    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"  {files_added} Dateien gesichert, {skipped} übersprungen")
    print(f"  Archivgröße: {size_mb:.1f} MB")
    print()

    # Version speichern
    entry = {
        "version":  ver_nr,
        "filename": name,
        "date":     date_hr,
        "files":    files_added,
        "size_mb":  round(size_mb, 1),
        "note":     note,
    }
    data["version"] = ver_nr
    data["backups"].append(entry)
    save_version(data)

    print(f"  ✅ Backup erfolgreich erstellt: {name}")
    print(f"{'='*60}\n")


# ── Backup-Liste anzeigen ─────────────────────────────────────────────────────
def list_backups() -> None:
    data = load_version()
    if not data["backups"]:
        print("\n  Keine Backups vorhanden.\n")
        return

    print(f"\n{'='*70}")
    print(f"  YCONN Backup-Übersicht  –  {len(data['backups'])} Backup(s)")
    print(f"{'='*70}")
    print(f"  {'Nr':>4}  {'Datum':<20} {'Größe':>7}  {'Dateien':>7}  Notiz")
    print(f"  {'-'*62}")
    for b in data["backups"]:
        note = b.get("note", "")
        print(
            f"  {b['version']:>4}  {b['date']:<20} "
            f"{b['size_mb']:>5.1f}MB  {b['files']:>7}  {note}"
        )
    print(f"{'='*70}")
    print(f"  Speicherort: {BACKUP_DIR}\n")


# ── Backup wiederherstellen ───────────────────────────────────────────────────
def restore_backup(version_nr: int) -> None:
    data = load_version()
    entry = next((b for b in data["backups"] if b["version"] == version_nr), None)
    if not entry:
        print(f"\n  ❌ Backup Nr. {version_nr} nicht gefunden.\n")
        list_backups()
        return

    zip_path = BACKUP_DIR / entry["filename"]
    if not zip_path.exists():
        print(f"\n  ❌ Datei nicht gefunden: {zip_path}\n")
        return

    print(f"\n{'='*60}")
    print(f"  Wiederherstellen: {entry['filename']}")
    print(f"  Datum: {entry['date']}")
    print(f"  WARNUNG: Aktuelle Dateien werden überschrieben!")
    print(f"{'='*60}")
    confirm = input("  Fortfahren? (ja/nein): ").strip().lower()
    if confirm not in ("ja", "j", "yes", "y"):
        print("  Abgebrochen.\n")
        return

    print(f"\n  Entpacke nach {APP_ROOT} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(APP_ROOT)
    print(f"  ✅ Wiederhergestellt: {entry['filename']}\n")


# ── Alte Backups aufräumen (behalte letzten N) ────────────────────────────────
def cleanup_old_backups(keep: int = 10) -> None:
    data = load_version()
    if len(data["backups"]) <= keep:
        return
    to_delete = data["backups"][:-keep]
    for entry in to_delete:
        f = BACKUP_DIR / entry["filename"]
        if f.exists():
            f.unlink()
            print(f"  🗑 Altes Backup gelöscht: {entry['filename']}")
    data["backups"] = data["backups"][-keep:]
    save_version(data)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YCONN App Backup")
    parser.add_argument("--list",    action="store_true", help="Vorhandene Backups anzeigen")
    parser.add_argument("--restore", type=int, metavar="NR", help="Backup Nr. wiederherstellen")
    parser.add_argument("--note",    default="", help="Notiz zum Backup (optional)")
    parser.add_argument("--keep",    type=int, default=20, help="Max. Backups behalten (default: 20)")
    args = parser.parse_args()

    if args.list:
        list_backups()
    elif args.restore:
        restore_backup(args.restore)
    else:
        create_backup(note=args.note)
        cleanup_old_backups(keep=args.keep)
