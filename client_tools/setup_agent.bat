@echo off
title SMRITI Retail OS - Printer Agent Installer
echo ===================================================
echo   SMRITI Retail OS - Windows Print Agent Setup     
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python (3.8 or higher) on this system first.
    echo Make sure to check the option "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Python installation detected.
echo [2/3] Installing required package 'pywin32'...
echo.
python -m pip install --upgrade pip
python -m pip install pywin32
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Direct pip install failed. Retrying with --user flag...
    python -m pip install --user pywin32
)

echo.
echo [3/3] Registering printer components...
:: Run post-install script of pywin32 to register DLLs
python -c "import win32api" >nul 2>&1
if %errorlevel% neq 0 (
    echo Running pywin32 post-install configuration...
    python "%cd%\..\..\..\Scripts\pywin32_postinstall.py" -install >nul 2>&1
)

echo.
echo ===================================================
echo   SETUP COMPLETED SUCCESSFULLY!                     
echo ===================================================
echo.
echo You can now run the Print Agent using 'run_agent.bat'.
echo To auto-start this agent on boot, copy 'run_agent.bat'
echo to your Windows Startup folder:
echo (Press Win+R, type 'shell:startup' and paste a shortcut there)
echo.
pause
