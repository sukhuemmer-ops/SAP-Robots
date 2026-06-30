@echo off
cd /d "%~dp0"
echo === SAP-Robots Git Auto-Sync ===
echo.

REM watchdog installieren falls noetig
worker\.venv\Scripts\python.exe -m pip show watchdog >nul 2>nul
if errorlevel 1 (
    echo Installiere watchdog...
    worker\.venv\Scripts\python.exe -m pip install watchdog
)

echo Beobachte Aenderungen -- Strg+C zum Beenden
echo.
worker\.venv\Scripts\python.exe git_autosync.py
pause
