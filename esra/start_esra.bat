@echo off
title ESRA – Intelligenter SAP Assistent
cd /d "%~dp0"

REM ----- 1. Python prüfen -----
where python >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python nicht im PATH.
    pause
    exit /b 1
)

REM ----- 2. venv anlegen falls nicht vorhanden -----
if not exist ".venv\Scripts\python.exe" (
    echo === Lege virtuelle Umgebung an ===
    python -m venv .venv
)

REM ----- 3. Pakete installieren -----
echo === Prüfe / installiere Abhängigkeiten ===
".venv\Scripts\pip.exe" install -q -r requirements.txt

REM ----- 4. anthropic explizit sicherstellen -----
".venv\Scripts\python.exe" -c "import anthropic" >nul 2>nul
if errorlevel 1 (
    echo === Installiere anthropic (KI-Paket) ===
    ".venv\Scripts\pip.exe" install anthropic openai -q
)

REM ----- 5. Esra starten -----
echo === Starte ESRA ===
".venv\Scripts\python.exe" esra_app.py
pause
