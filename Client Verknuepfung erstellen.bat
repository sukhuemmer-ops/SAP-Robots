@echo off
title YCONN – Desktop-Verknuepfung erstellen
color 0B

echo.
echo  ============================================================
echo   YCONN – Desktop-Verknuepfung fuer Netzwerk-Benutzer
echo  ============================================================
echo.

REM Server-IP abfragen
set /p "SERVER_IP=Bitte Server-IP eingeben (z.B. 192.168.1.100): "
if "%SERVER_IP%"=="" (
    echo Keine IP eingegeben. Abbruch.
    pause & exit /b 1
)

set "URL=http://%SERVER_IP%:8000/cockpit/login.html"
set "SHORTCUT=%USERPROFILE%\Desktop\YCONN Finance.url"

REM .url Datei erstellen (Browser-Lesezeichen als Desktopverknüpfung)
(
echo [InternetShortcut]
echo URL=%URL%
echo IconIndex=0
echo HotKey=0
) > "%SHORTCUT%"

echo.
echo  ============================================================
echo   OK – Desktop-Verknuepfung erstellt:
echo   %SHORTCUT%
echo.
echo   URL: %URL%
echo.
echo   Benutzer koennen sich jetzt ueber diese Verknuepfung
echo   im YCONN Cockpit anmelden.
echo  ============================================================
echo.
pause
