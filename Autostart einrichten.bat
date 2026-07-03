@echo off
title YCONN – Autostart einrichten (Task Scheduler)
color 0B

echo.
echo  ============================================================
echo   YCONN – Autostart bei Windows-Anmeldung einrichten
echo   Orchestrator + Bridge starten automatisch im Hintergrund
echo  ============================================================
echo.

REM Administratorrechte prüfen
net session >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Administrator-Rechte erforderlich.
    echo  Rechtsklick → Als Administrator ausfuehren
    pause
    exit /b 1
)

set "ROOT=%~dp0"
set "ORCH_SCRIPT=%ROOT%orchestrator\start_service.bat"
set "BRDG_SCRIPT=%ROOT%worker\start_service.bat"

REM Alte Tasks entfernen
schtasks /delete /tn "YCONN_Orchestrator" /f >nul 2>&1
schtasks /delete /tn "YCONN_Bridge"       /f >nul 2>&1

echo  Registriere Task: YCONN_Orchestrator...
schtasks /create ^
  /tn "YCONN_Orchestrator" ^
  /tr "\"%ORCH_SCRIPT%\"" ^
  /sc ONLOGON ^
  /rl HIGHEST ^
  /delay 0000:10 ^
  /f
if errorlevel 1 ( echo  FEHLER Orchestrator & pause & exit /b 1 )

echo  Registriere Task: YCONN_Bridge...
schtasks /create ^
  /tn "YCONN_Bridge" ^
  /tr "\"%BRDG_SCRIPT%\"" ^
  /sc ONLOGON ^
  /rl HIGHEST ^
  /delay 0000:20 ^
  /f
if errorlevel 1 ( echo  FEHLER Bridge & pause & exit /b 1 )

echo.
echo  ============================================================
echo   OK – Autostart eingerichtet!
echo.
echo   Beim naechsten Windows-Login starten automatisch:
echo   - YCONN_Orchestrator  (Port 8000) nach 10 Sekunden
echo   - YCONN_Bridge        (Port 8765) nach 20 Sekunden
echo.
echo   Tipp: Nach Einrichtung PC neu starten und pruefen:
echo   http://localhost:8000/cockpit/startseite.html
echo  ============================================================
echo.

REM Sofort starten?
set /p "START=Dienste jetzt sofort starten? (J/N): "
if /i "%START%"=="J" (
    start "" /min "%ORCH_SCRIPT%"
    timeout /t 10 /nobreak >nul
    start "" /min "%BRDG_SCRIPT%"
    echo  Dienste wurden gestartet.
)

pause
