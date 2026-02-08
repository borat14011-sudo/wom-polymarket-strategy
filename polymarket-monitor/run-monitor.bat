@echo off
REM Polymarket Monitor - Start Script (Windows)

echo Starting Polymarket Volume Monitor...
echo.

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Using: python
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import requests; import schedule" >nul 2>&1
if %errorlevel% neq 0 (
    echo Missing dependencies. Installing...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed
)

echo.
echo Starting monitor daemon...
echo Press Ctrl+C to stop
echo.

REM Run the daemon
python monitor_daemon.py
