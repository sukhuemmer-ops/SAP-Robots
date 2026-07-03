@echo off
REM YCONN Bridge – stiller Wrapper fuer Task Scheduler / Autostart
cd /d "%~dp0"
del /q __pycache__\handlers.cpython-*.pyc 2>nul
python bridge.py
