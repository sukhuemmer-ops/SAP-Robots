@echo off
cd /d "%~dp0worker"
echo.
echo === Python-Cache leeren (verhindert veralteten handlers.pyc) ===
if exist "__pycache__\handlers.cpython-*.pyc" (
    del /q "__pycache__\handlers.cpython-*.pyc" 2>nul
    echo     handlers.pyc geloescht - wird neu kompiliert.
) else (
    echo     Kein alter Cache gefunden.
)
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
