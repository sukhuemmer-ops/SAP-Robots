@echo off
cd /d "%~dp0worker"
echo.
echo === Abhängigkeiten prüfen (anthropic, openai) ===
".venv\Scripts\pip.exe" install anthropic openai -q --disable-pip-version-check 2>nul
echo.
echo === Cockpit-Bridge startet ===
echo === Strg+C zum Stoppen ===
echo.
".venv\Scripts\python.exe" bridge.py
echo.
echo === Bridge beendet ===
pause
