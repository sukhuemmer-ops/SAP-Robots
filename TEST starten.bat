@echo off
title YCONN - TEST (SAP SEQ - Quality Assurance)
color 09
echo.
echo  ==================================================
echo   YCONN Finance-Assistent - TESTUMGEBUNG
echo   SAP-Verbindung: SEQ  172.28.189.11  (Quality Assurance)
echo  ==================================================
echo.

python env_switch.py test
if errorlevel 1 ( pause & exit /b 1 )

echo.
echo  Starte Dienste...
echo.

start "YCONN Orchestrator [TEST]" cmd /k "cd /d %~dp0orchestrator && echo [TEST] Orchestrator startet... && uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

start "YCONN Bridge [TEST]" cmd /k "cd /d %~dp0worker && echo [TEST] Bridge startet... && python bridge.py"
timeout /t 2 /nobreak >nul

set /p VOICE="Voice Server starten? [j/n]: "
if /i "%VOICE%"=="j" (
    start "YCONN Voice [TEST]" cmd /k "cd /d %~dp0worker && uvicorn voice_server:app --port 8766"
)

start "" "%~dp0cockpit\startseite.html"

echo.
echo  ✓ TESTUMGEBUNG gestartet  ^(SAP SEQ^)
echo    Orchestrator: http://localhost:8000
echo    Bridge:       http://localhost:8765
echo    SAP:          SEQ 172.28.189.11 (QA)
echo.
pause
