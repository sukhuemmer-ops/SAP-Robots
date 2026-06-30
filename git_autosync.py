"""
Git Auto-Sync für SAP-Robots
Beobachtet Dateiänderungen und pusht automatisch nach GitHub.
Debounce: 30 Sekunden nach letzter Änderung.
"""
import subprocess
import sys
import time
import os
from pathlib import Path
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Installiere watchdog...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

ROOT = Path(__file__).resolve().parent
DEBOUNCE = 30  # Sekunden nach letzter Änderung

# Pfade die ignoriert werden
IGNORE = {
    ".git", "__pycache__", ".venv", "reports", "invoices",
    "rechnungen", ".db", ".log", ".tmp", ".bak", "~$"
}


def should_ignore(path: str) -> bool:
    p = Path(path)
    for part in p.parts:
        if part in IGNORE:
            return True
    for ign in IGNORE:
        if p.name.endswith(ign) or p.name.startswith("~$"):
            return True
    return False


def git_sync():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n[{now}] Änderungen erkannt — synchronisiere...", flush=True)
    try:
        subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT
        )
        if result.returncode == 0:
            print("  Keine neuen Änderungen zum committen.", flush=True)
            return
        subprocess.run(
            ["git", "commit", "-m", f"Auto-Sync {now}"],
            cwd=ROOT, check=True
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=ROOT, check=True
        )
        print(f"  ✓ Erfolgreich gepusht nach GitHub.", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Git-Fehler: {e}", flush=True)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self._last_change = 0

    def on_any_event(self, event):
        if event.is_directory:
            return
        if should_ignore(event.src_path):
            return
        self._last_change = time.time()

    def pending(self):
        return self._last_change > 0

    def ready_to_sync(self):
        if self._last_change == 0:
            return False
        return (time.time() - self._last_change) >= DEBOUNCE

    def reset(self):
        self._last_change = 0


if __name__ == "__main__":
    print("=== SAP-Robots Git Auto-Sync ===")
    print(f"  Verzeichnis: {ROOT}")
    print(f"  Remote:      github.com/sukhuemmer-ops/SAP-Robots")
    print(f"  Debounce:    {DEBOUNCE} Sekunden nach letzter Änderung")
    print("  Strg+C zum Beenden")
    print()

    handler = ChangeHandler()
    observer = Observer()
    observer.schedule(handler, str(ROOT), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(5)
            if handler.ready_to_sync():
                handler.reset()
                git_sync()
    except KeyboardInterrupt:
        print("\n=== Auto-Sync beendet ===")
        observer.stop()
    observer.join()
