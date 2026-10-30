@echo off
setlocal
cd /d "%~dp0"
title Shorts Studio
if not exist ".venv\Scripts\python.exe" (
    echo Preparing Python environment for first use...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo Python 3.10 or newer is required. Install Python and try again.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" -c "import flask, moviepy, edge_tts" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages. Please wait...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" launch.py
if errorlevel 1 (
    echo Please check the error message above.
    pause
    exit /b 1
)
endlocal
