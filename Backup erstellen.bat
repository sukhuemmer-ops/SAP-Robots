@echo off
title YCONN - Backup erstellen

cd /d "%~dp0"

echo.
echo  ==========================================
echo   YCONN App Backup
echo  ==========================================
echo.

set NOTE=
set /p NOTE=  Notiz zum Backup (Enter = leer):

echo.

python backup.py --note "%NOTE%"

if %errorlevel% neq 0 (
    echo.
    echo  FEHLER beim Erstellen des Backups!
    echo.
    pause
    exit /b 1
)

echo.
echo  Backup gespeichert in: %~dp0backups\
echo.
pause
