"""
YCONN Umgebungs-Umschalter
============================
Kopiert .env.dev / .env.test / .env.prod → .env
für worker/ und orchestrator/

Verwendung:
    python env_switch.py dev
    python env_switch.py test
    python env_switch.py prod
    python env_switch.py status   ← zeigt aktive Umgebung
"""
import sys
import shutil
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DIRS = {
    "worker":       ROOT / "worker",
    "orchestrator": ROOT / "orchestrator",
}

LABELS = {
    "dev":  "🟢 ENTWICKLUNG   → SAP SEQ 172.28.189.11 (Quality Assurance)",
    "test": "🔵 TEST           → SAP SEQ 172.28.189.11 (Quality Assurance)",
    "prod": "🔴 PRODUKTION     → SAP SEP 172.28.189.8  (Produktivsystem)",
}


def current_env(directory: Path) -> str:
    env_file = directory / ".env"
    if not env_file.exists():
        return "(keine .env)"
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("APP_ENV="):
            return line.split("=", 1)[1].strip()
    return "(unbekannt)"


def switch(target: str) -> None:
    if target not in LABELS:
        print(f"❌ Unbekannte Umgebung: '{target}'. Erlaubt: dev | test | prod")
        sys.exit(1)

    # Sicherheitsabfrage für PROD
    if target == "prod":
        print("⚠  ACHTUNG: Sie wechseln in die PRODUKTIVUMGEBUNG!")
        print("   Alle SAP-Aktionen wirken auf SEP 172.28.189.8 (Produktivsystem).")
        answer = input("   Wirklich wechseln? [ja/nein]: ").strip().lower()
        if answer not in ("ja", "j", "yes", "y"):
            print("Abgebrochen.")
            return

    switched = []
    for name, directory in DIRS.items():
        src = directory / f".env.{target}"
        dst = directory / ".env"
        if not src.exists():
            print(f"⚠  {name}/.env.{target} nicht gefunden – übersprungen")
            continue
        # Backup der aktuellen .env
        if dst.exists():
            backup = directory / f".env.backup"
            shutil.copy2(dst, backup)
        shutil.copy2(src, dst)
        switched.append(name)

    if switched:
        print(f"\n✅ Umgebung gewechselt → {LABELS[target]}")
        print(f"   Betroffen: {', '.join(switched)}")
        print(f"\n   Bitte alle laufenden Dienste neu starten:")
        print(f"   Orchestrator, Bridge und Voice Server.")
    else:
        print("❌ Keine Dateien kopiert – prüfen Sie ob .env.{target} existiert.")


def status() -> None:
    print("\n── Aktive Umgebungen ─────────────────────────────────────")
    for name, directory in DIRS.items():
        env = current_env(directory)
        label = LABELS.get(env, f"({env})")
        print(f"  {name:15} → {label}")
    print()
    print("── Verfügbare Umgebungen ─────────────────────────────────")
    for env, label in LABELS.items():
        print(f"  {env:6} → {label}")
    print()
    print("Wechseln mit:  python env_switch.py [dev|test|prod]")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("status", "-s", "--status"):
        status()
    else:
        switch(sys.argv[1].lower())
