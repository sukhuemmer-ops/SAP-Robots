@echo off
REM Startet den Worker fuer Robot-AP. Fuer AR / GL / AA kopiere diese Datei
REM und aendere die Variable ROBOT_ID auf AR, GL oder AA.

cd /d "%~dp0worker"

REM ----- 1. Python finden -----
where python >nul 2>nul
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH.
    pause
    exit /b 1
)

REM ----- 2. venv anlegen, falls noch nicht da -----
if not exist ".venv\Scripts\python.exe" (
    echo === Lege virtuelle Umgebung an ===
    python -m venv .venv
    if errorlevel 1 (
        echo FEHLER beim Anlegen der virtuellen Umgebung.
        pause
        exit /b 1
    )
)

REM ----- 3. Abhaengigkeiten pruefen / installieren -----
".venv\Scripts\python.exe" -m pip show requests >nul 2>nul
if errorlevel 1 (
    echo === Installiere Abhaengigkeiten ===
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo FEHLER bei pip install.
        pause
        exit /b 1
    )
    echo.
    echo HINWEIS: Fuer echte SAP-Calls zusaetzlich installieren (nur auf VM mit SAP GUI):
    echo   .venv\Scripts\python.exe -m pip install pywin32 pyrfc
    echo.
)

set ROBOT_ID=AP
set WORKER_ID=worker-ap-local
set ORCHESTRATOR_URL=http://localhost:8000

echo === Worker %WORKER_ID% startet (Robot=%ROBOT_ID%) ===
echo === Strg+C zum Stoppen ===
".venv\Scripts\python.exe" worker.py
pause
