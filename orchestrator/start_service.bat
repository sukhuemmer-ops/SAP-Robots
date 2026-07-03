@echo off
REM YCONN Orchestrator – stiller Wrapper fuer Task Scheduler / Autostart
REM Kein sichtbares Fenster, kein Benutzereingriff noetig.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -q --upgrade pip
    .venv\Scripts\python.exe -m pip install -q -r requirements.txt
)
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
