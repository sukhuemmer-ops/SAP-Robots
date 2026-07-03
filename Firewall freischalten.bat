@echo off
title YCONN – Windows Firewall Ports freischalten
color 0A

echo.
echo  ============================================================
echo   YCONN – Windows Firewall Konfiguration
echo   Ports 8000 (Orchestrator) und 8765 (Bridge) freischalten
echo  ============================================================
echo.

REM Administratorrechte prüfen
net session >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Dieses Script muss als Administrator ausgefuehrt werden!
    echo  Rechtsklick auf die .bat → Als Administrator ausfuehren
    echo.
    pause
    exit /b 1
)

echo  Loesche alte YCONN-Regeln (falls vorhanden)...
netsh advfirewall firewall delete rule name="YCONN Orchestrator Port 8000" >nul 2>&1
netsh advfirewall firewall delete rule name="YCONN Bridge Port 8765" >nul 2>&1
netsh advfirewall firewall delete rule name="YCONN Voice Port 8766" >nul 2>&1

echo  Erstelle Eingangsregeln...
netsh advfirewall firewall add rule ^
  name="YCONN Orchestrator Port 8000" ^
  dir=in protocol=TCP localport=8000 action=allow ^
  profile=domain,private description="YCONN SAP Finance Robots - Orchestrator API"
if errorlevel 1 goto :FEHLER

netsh advfirewall firewall add rule ^
  name="YCONN Bridge Port 8765" ^
  dir=in protocol=TCP localport=8765 action=allow ^
  profile=domain,private description="YCONN SAP Finance Robots - SAP Bridge"
if errorlevel 1 goto :FEHLER

netsh advfirewall firewall add rule ^
  name="YCONN Voice Port 8766" ^
  dir=in protocol=TCP localport=8766 action=allow ^
  profile=domain,private description="YCONN SAP Finance Robots - Voice Server"
if errorlevel 1 goto :FEHLER

echo.
echo  ============================================================
echo   OK - Firewall-Regeln erstellt:
echo.
echo   Port 8000  Orchestrator + Cockpit-Webseite (Netzwerk)
echo   Port 8765  SAP Bridge (Buchungsverbindung)
echo   Port 8766  Voice-Server (Esra Sprachassistentin)
echo.
echo   Netzwerk-Benutzer koennen das Cockpit jetzt ueber
echo   http://<SERVER-IP>:8000/cockpit/startseite.html
echo   im Browser oeffnen.
echo  ============================================================
echo.
pause
exit /b 0

:FEHLER
echo.
echo  FEHLER beim Erstellen der Firewall-Regeln!
echo  Bitte Administrator-Rechte pruefen.
pause
exit /b 1
