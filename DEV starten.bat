@echo off
title YCONN - ENTWICKLUNG (SAP SEQ)
color 0A
echo.
echo  ==================================================
echo   YCONN Finance-Assistent - ENTWICKLUNGSUMGEBUNG
echo   SAP-Verbindung: SEQ  172.28.189.11  (Quality Assurance)
echo  ==================================================
echo.

python env_switch.py dev
if errorlevel 1 ( pause & exit /b 1 )

echo.
echo  Starte Dienste...
echo.

start "YCONN Orchestrator [DEV]" cmd /k "cd /d %~dp0orchestrator && echo [DEV] Orchestrator startet... && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

start "YCONN Bridge [DEV]" cmd /k "cd /d %~dp0worker && echo [DEV] Bridge startet... && python bridge.py"
timeout /t 2 /nobreak >nul

start "" "%~dp0cockpit\startseite.html"

echo.
echo  ✓ ENTWICKLUNG gestartet  ^(SAP SEQ^)
echo    Orchestrator: http://localhost:8000
echo    Bridge:       http://localhost:8765
echo.
pause
