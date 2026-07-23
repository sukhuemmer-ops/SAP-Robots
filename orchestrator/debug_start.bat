@echo off
title YCONN Orchestrator - DEBUG START
cd /d "%~dp0"

echo ============================================
echo  YCONN Orchestrator - Debug-Start
echo ============================================
echo.

REM PyCache loeschen (verhindert Laden alter .pyc-Dateien)
echo Loesche __pycache__ ...
if exist "__pycache__" rd /s /q "__pycache__"

echo.
echo Pruefe Python ...
.venv\Scripts\python.exe --version
if errorlevel 1 (
    echo FEHLER: .venv nicht gefunden, versuche System-Python ...
    python --version
)

echo.
echo Pruefe main.py Syntax ...
.venv\Scripts\python.exe -c "import ast; ast.parse(open('main.py',encoding='utf-8').read()); print('Syntax OK')"
if errorlevel 1 (
    echo FEHLER: Syntaxfehler in main.py
    pause
    exit /b 1
)

echo.
echo Starte Orchestrator (Port 8000) ...
echo Fehler werden direkt angezeigt.
echo.
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level debug

echo.
echo ============================================
echo  Orchestrator beendet (Exitcode: %errorlevel%)
echo ============================================
pause
