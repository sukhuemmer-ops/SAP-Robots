"""
SAP Robot Worker
================
Laeuft auf einer Windows-VM mit:
  * installiertem SAP GUI (fuer GUI-Scripting-Tasks)
  * SAP NW RFC SDK (fuer pyrfc / BAPI-Tasks)
  * Netzwerk-Zugriff auf das SAP-System

Der Worker pollt den Orchestrator nach offenen Jobs ("queued"), fuehrt sie aus
und meldet das Ergebnis zurueck. Pro Robot (AP/AR/GL/AA) wird typischerweise
ein eigener Worker-Prozess gestartet -- mit eigenem SAP-Service-User und
eigenen Berechtigungen.

Konfiguration ueber Umgebungsvariablen. Die Datei ``.env`` (oder als Fallback
``.env.example``) im Worker-Ordner wird beim Start automatisch geladen.

Start:
    set ROBOT_ID=AP
    set ORCHESTRATOR_URL=http://localhost:8000
    python worker.py
"""
from __future__ import annotations

import json
import logging
import os
import time
import traceback
from pathlib import Path
from typing import Optional

import requests

# .env-Loader (python-dotenv) - laedt Datei beim Start, falls vorhanden
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    here = Path(__file__).resolve().parent
    for candidate in (here / ".env", here / ".env.example"):
        if candidate.exists():
            load_dotenv(candidate)
            break

from handlers import HANDLERS  # noqa: E402  (nach load_dotenv, damit Env-Werte da sind)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("worker")

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
ROBOT_ID = os.getenv("ROBOT_ID", "AP")
WORKER_ID = os.getenv("WORKER_ID", f"worker-{ROBOT_ID.lower()}-local")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "5"))


def claim_run() -> Optional[dict]:
    r = requests.post(
        f"{ORCHESTRATOR_URL}/worker/claim",
        params={"worker_id": WORKER_ID, "robot_id": ROBOT_ID},
        timeout=10,
    )
    r.raise_for_status()
    return r.json() or None


def report(run_id: int, status: str, log_text: str = "") -> None:
    requests.post(
        f"{ORCHESTRATOR_URL}/worker/runs/{run_id}",
        json={"status": status, "log": log_text, "worker_id": WORKER_ID},
        timeout=10,
    )


def fetch_task(task_id: int) -> dict:
    r = requests.get(f"{ORCHESTRATOR_URL}/tasks", params={"robot_id": ROBOT_ID}, timeout=10)
    r.raise_for_status()
    for t in r.json():
        if t["id"] == task_id:
            return t
    raise RuntimeError(f"Task {task_id} nicht im Orchestrator gefunden.")


def execute(task: dict, payload: dict) -> str:
    key = (task["method"], task["tcode"])
    handler = (HANDLERS.get(key)
               or HANDLERS.get(("*", task["tcode"]))
               or HANDLERS.get((task["method"], "*")))
    if not handler:
        raise RuntimeError(f"Kein Handler fuer {task['method']} / {task['tcode']}")
    return handler(task, payload)


def loop_once() -> None:
    run = claim_run()
    if not run:
        return
    run_id = run["id"]
    log.info("Job %d uebernommen (Task %s).", run_id, run["task_id"])
    try:
        task = fetch_task(run["task_id"])
        payload = json.loads(task.get("parameters") or "{}")
        report(run_id, "running", f"Worker {WORKER_ID} startet {task['name']} ({task['tcode']}).")
        result_log = execute(task, payload)
        report(run_id, "ok", result_log or "Erfolgreich abgeschlossen.")
        log.info("Job %d erfolgreich.", run_id)
    except Exception as exc:  # noqa: BLE001
        tb = traceback.format_exc()
        log.error("Job %d fehlgeschlagen: %s", run_id, exc)
        report(run_id, "error", f"{exc}\n{tb}")


def main() -> None:
    log.info("Worker %s startet (Robot=%s, Orchestrator=%s)", WORKER_ID, ROBOT_ID, ORCHESTRATOR_URL)
    while True:
        try:
            loop_once()
        except requests.RequestException as exc:
            log.warning("Orchestrator nicht erreichbar: %s", exc)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
