@echo off
title ESRA – Intelligenter SAP Assistent
cd /d "%~dp0"

echo Prüfe Abhängigkeiten...
pip install -q -r requirements.txt --break-system-packages 2>nul || pip install -q -r requirements.txt

echo Starte ESRA...
python esra_app.py
pause
