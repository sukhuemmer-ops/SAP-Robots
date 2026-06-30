@echo off
cd /d "%~dp0worker"
echo.
echo === Cockpit-Bridge startet ===
echo === Strg+C zum Stoppen ===
echo.
".venv\Scripts\python.exe" bridge.py
echo.
echo === Bridge beendet ===
pause
