@echo off
REM Startet den FastAPI-Orchestrator auf Port 8000.
REM Erforderlich: Python 3.10+ installiert und im PATH.

cd /d "%~dp0orchestrator"

REM ----- 1. Python finden -----
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo FEHLER: Python ist nicht installiert oder nicht im PATH.
    echo Bitte Python 3.12 oder 3.13 von https://www.python.org installieren
    echo und beim Setup "Add Python to PATH" anhaken.
    echo HINWEIS: Python 3.14 funktioniert noch nicht mit allen Bibliotheken.
    echo.
    pause
    exit /b 1
)

REM ----- 2. venv anlegen, falls noch nicht da -----
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo === Lege virtuelle Umgebung an ===
    python -m venv .venv
    if errorlevel 1 (
        echo FEHLER beim Anlegen der virtuellen Umgebung.
        pause
        exit /b 1
    )
)

REM ----- 3. Abhaengigkeiten pruefen / installieren -----
".venv\Scripts\python.exe" -m pip show uvicorn >nul 2>nul
if errorlevel 1 (
    echo.
    echo === Installiere Abhaengigkeiten (1-2 Minuten beim ersten Mal) ===
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install --upgrade -r requirements.txt
    if errorlevel 1 (
        echo.
        echo FEHLER bei pip install.
        echo.
        echo Moegliche Loesungen:
        echo   1. venv loeschen und neu probieren:
        echo        rmdir /s /q .venv
        echo      Danach diese .bat erneut starten.
        echo   2. Falls du Python 3.14 nutzt: deinstallieren und 3.12 oder 3.13 installieren.
        echo      Python 3.14 ist zu neu fuer manche Bibliotheken.
        echo.
        pause
        exit /b 1
    )
)

REM ----- 4. Python-Cache loeschen (verhindert veralteten main.pyc) -----
if exist "__pycache__\main.cpython-*.pyc" (
    del /q "__pycache__\main.cpython-*.pyc" 2>nul
    echo     main.pyc Cache geloescht.
)

echo.
echo === Orchestrator startet auf http://localhost:8000 ===
echo === API-Doku:    http://localhost:8000/docs ===
echo === Strg+C zum Stoppen ===
echo.
".venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000
pause
