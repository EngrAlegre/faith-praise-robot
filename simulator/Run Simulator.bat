@echo off
title Five Sides - robot simulator
cd /d "%~dp0"

set PY=C:\Users\isaac\AppData\Local\Programs\Python\Python312\pythonw.exe
if not exist "%PY%" set PY=pythonw

start "" "%PY%" five_sides_sim.py
if errorlevel 1 (
  echo The simulator did not start. Running in a console to show the error...
  python five_sides_sim.py
  pause
)
