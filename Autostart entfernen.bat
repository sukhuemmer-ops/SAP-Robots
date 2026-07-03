@echo off
title YCONN – Autostart entfernen
color 0C

net session >nul 2>&1
if errorlevel 1 (
    echo Administratorrechte erforderlich. Rechtsklick → Als Administrator.
    pause & exit /b 1
)

schtasks /delete /tn "YCONN_Orchestrator" /f >nul 2>&1 && echo Orchestrator-Task entfernt. || echo Orchestrator-Task nicht gefunden.
schtasks /delete /tn "YCONN_Bridge"       /f >nul 2>&1 && echo Bridge-Task entfernt.       || echo Bridge-Task nicht gefunden.

echo.
echo Autostart deaktiviert.
pause
