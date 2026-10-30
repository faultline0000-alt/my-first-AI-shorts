@echo off
setlocal
cd /d "%~dp0"
title Shorts Studio
if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found.
    echo Follow the Windows installation steps in README.md first.
    echo Run: py -m venv .venv
    echo Then: .venv\Scripts\python -m pip install -r requirements.txt
    pause
    exit /b 1
)
".venv\Scripts\python.exe" launch.py
if errorlevel 1 (
    echo Please check the error message above.
    pause
    exit /b 1
)
endlocal
