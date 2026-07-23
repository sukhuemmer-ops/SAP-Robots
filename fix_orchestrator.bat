@echo off
title Orchestrator Reparatur
echo.
echo  ========================================
echo   Orchestrator - Cache leeren + Pruefen
echo  ========================================
echo.

cd /d "%~dp0orchestrator"

REM ---- Alle .pyc-Cache-Dateien loeschen ----
echo  [1] Loesche Python-Cache (__pycache__)...
rd /s /q __pycache__ 2>nul
echo      Cache geloescht.
echo.

REM ---- Syntax-Pruefung ----
echo  [2] Pruefe main.py Syntax...
".venv\Scripts\python.exe" -c "
import ast, sys
try:
    src = open('main.py', encoding='utf-8').read()
    ast.parse(src)
    lines = src.splitlines()
    print(f'  OK - {len(lines)} Zeilen, Syntax fehlerfrei')
except SyntaxError as e:
    print(f'  FEHLER in Zeile {e.lineno}: {e.msg}')
    print(f'  Text: {e.text}')
    sys.exit(1)
"
if errorlevel 1 (
    echo.
    echo  Syntax-Fehler gefunden. Versuche automatische Reparatur...
    ".venv\Scripts\python.exe" "%~dp0fix_main.py"
    echo.
    echo  Erneute Pruefung nach Reparatur:
    ".venv\Scripts\python.exe" -c "
import ast, sys
try:
    src = open('main.py', encoding='utf-8').read()
    ast.parse(src)
    print('  OK - Reparatur erfolgreich')
except SyntaxError as e:
    print(f'  NOCH Fehler: Zeile {e.lineno}: {e.msg}')
    sys.exit(1)
"
    if errorlevel 1 (
        echo.
        echo  Automatische Reparatur fehlgeschlagen.
        echo  Bitte Selko kontaktieren.
        pause
        exit /b 1
    )
)

echo.
echo  [3] Starte Orchestrator...
echo.
echo  === Orchestrator auf http://localhost:8000 ===
echo  === Strg+C zum Stoppen ===
echo.
".venv\Scripts\python.exe" -m uvicorn main:app --reload --port 8000
pause
