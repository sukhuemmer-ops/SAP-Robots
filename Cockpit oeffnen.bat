@echo off
REM Doppelklick: oeffnet das Cockpit ueber die Bridge (http://localhost:8765)
REM Die Bridge muss laufen (Bridge starten.bat), sonst Fallback auf Datei.
ping -n 1 -w 500 127.0.0.1 >nul 2>nul
curl -s --max-time 1 http://localhost:8765/health >nul 2>nul
if %errorlevel%==0 (
    start "" "http://localhost:8765/"
) else (
    echo Bridge nicht erreichbar - oeffne als Datei (kein Login-Schutz)
    start "" "%~dp0cockpit\login.html"
)
