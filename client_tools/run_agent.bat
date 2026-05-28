@echo off
title SMRITI Print Agent
cd /d "%~dp0"
python windows_auto_print.py
if %errorlevel% neq 0 (
    echo.
    echo Print Agent crashed or failed to start.
    echo Make sure Python and pywin32 are installed correctly.
    echo Run 'setup_agent.bat' to fix missing packages.
    echo.
    pause
)
