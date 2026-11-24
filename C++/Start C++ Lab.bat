@echo off
REM Start the C++ Lab and open it in the browser.
cd /d "%~dp0"

set PY=C:\Users\isaac\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PY%" set PY=python

start "" http://127.0.0.1:8765
"%PY%" server.py --port 8765
pause
