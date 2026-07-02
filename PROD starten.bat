@echo off
title YCONN - PRODUKTION (SAP SEP)
color 04
echo.
echo  ==================================================
echo   YCONN Finance-Assistent - PRODUKTIVUMGEBUNG
echo   SAP System: SEP  172.28.189.8  (Produktion)
echo.
echo   !!!  ACHTUNG - ECHTES SAP PRODUKTIVSYSTEM  !!!
echo   !!!  Buchungen wirken auf echte Daten!      !!!
echo  ==================================================
echo.
echo  Druecken Sie STRG+C um abzubrechen, oder...
timeout /t 5

python env_switch.py prod
if errorlevel 1 ( echo Abgebrochen. & pause & exit /b 1 )

echo.
echo  Starte Dienste...
echo.

start "YCONN Orchestrator [PROD]" cmd /k "cd /d %~dp0orchestrator && echo [PROD] Orchestrator startet... && uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

start "YCONN Bridge [PROD]" cmd /k "cd /d %~dp0worker && del /q __pycache__\handlers.cpython-*.pyc 2>nul && echo [PROD] Bridge startet... && python bridge.py"
timeout /t 2 /nobreak >nul

start "YCONN Voice [PROD]" cmd /k "cd /d %~dp0worker && uvicorn voice_server:app --port 8766"

start "" "%~dp0cockpit\startseite.html"

echo.
echo  ✓ PRODUKTIVUMGEBUNG gestartet  ^(SAP SEP^)
echo    Orchestrator: http://localhost:8000
echo    Bridge:       http://localhost:8765
echo    Voice:        http://localhost:8766
echo    SAP:          SEP 172.28.189.8 (Produktion)
echo.
pause
