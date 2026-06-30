@echo off
cd /d "%~dp0"
echo === GitHub Sync: sukhuemmer-ops/SAP-Robots ===
echo.

if not exist ".git" (
    git init
    git branch -M main
    echo === Git Repository initialisiert ===
)

git remote remove origin 2>nul
git remote add origin https://github.com/sukhuemmer-ops/SAP-Robots.git
echo === Remote: github.com/sukhuemmer-ops/SAP-Robots ===

git add -A
echo.
git status
echo.

set DATUM=%date:~6,4%-%date:~3,2%-%date:~0,2%
git commit -m "YCONN Cockpit Stand %DATUM%"

echo.
echo === Pushe nach GitHub... ===
git push -u origin main

echo.
if errorlevel 1 (
    echo === FEHLER beim Push! ===
) else (
    echo === Erfolgreich synchronisiert! ===
)
pause
