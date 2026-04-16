@echo off
REM Copilot Chat History Exporter - Windows Task Scheduler Setup
REM
REM This batch file creates a scheduled task to export Copilot chat history daily.
REM
REM NOTE: Run "python export_copilot_history.py --setup" first to configure preferences!

setlocal enabledelayedexpansion

REM ====== CONFIGURATION ======
REM These are only used if config file doesn't exist yet.
REM For first time: Run "python export_copilot_history.py --setup" to configure interactively

REM Full path to python.exe (leave blank to auto-detect)
SET PYTHON_PATH=

REM Full path to this folder (where export_copilot_history.py is located)
SET SCRIPT_DIR=%~dp0

REM ====== END CONFIGURATION ======

echo.
echo ========================================
echo Copilot Chat History - Task Scheduler Setup
echo ========================================
echo.

REM Auto-detect Python if not specified
if "!PYTHON_PATH!"=="" (
    for /f "tokens=*" %%i in ('where python.exe') do set PYTHON_PATH=%%i
    if "!PYTHON_PATH!"=="" (
        echo ERROR: Python not found. Install Python or set PYTHON_PATH manually.
        pause
        exit /b 1
    )
)

REM Check if script exists
if not exist "!SCRIPT_DIR!export_copilot_history.py" (
    echo ERROR: export_copilot_history.py not found in:
    echo   !SCRIPT_DIR!
    pause
    exit /b 1
)

echo Configuration:
echo   Python: !PYTHON_PATH!
echo   Script: !SCRIPT_DIR!export_copilot_history.py
echo.
echo NOTE: Output directory and export time are read from:
echo   %USERPROFILE%\.copilot_exporter_config.json
echo.
echo If this is your first time, run:
echo   python "!SCRIPT_DIR!export_copilot_history.py" --setup
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator.
    echo.
    echo Please right-click this batch file and select "Run as administrator"
    pause
    exit /b 1
)

REM Create or update the scheduled task
echo Creating scheduled task...
echo.

REM Task will be created to run daily - time is read from config file
schtasks /create /tn "Copilot Chat History Export" /tr "\"!PYTHON_PATH!\" \"!SCRIPT_DIR!export_copilot_history.py\"" /sc daily /st 23:00 /f

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Task created!
    echo.
    echo Task name: Copilot Chat History Export
    echo   Default time: 23:00 (can be customized via config)
    echo   Command: "!PYTHON_PATH!" "!SCRIPT_DIR!export_copilot_history.py"
    echo.
    echo To customize the export time:
    echo   1. Open Task Scheduler (taskschd.msc)
    echo   2. Find "Copilot Chat History Export"
    echo   3. Right-click and select "Properties" to edit the schedule
    echo   4. Or run "python export_copilot_history.py --setup" to reconfigure
    echo.
    echo To verify the task was created:
    echo   1. Open Task Scheduler (taskschd.msc)
    echo   2. Look for "Copilot Chat History Export" in the task list
    echo   3. Right-click and select "Run" to test it immediately
    echo.
) else (
    echo.
    echo ERROR: Failed to create task. Exit code: %errorlevel%
    echo.
)

pause
