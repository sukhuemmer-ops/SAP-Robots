@echo off
title YCONN - DB Migration nach Lokal
cd /d "%~dp0"
echo.
echo  Datenbank wird von Z:\DB\ nach C:\WF\sap-robots\orchestrator\ kopiert...
echo.
python db_migrate_lokal.py
if %errorlevel% neq 0 (
    echo.
    echo  FEHLER bei der Migration!
    pause
    exit /b 1
)
