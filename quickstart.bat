@echo off
REM Quick Start Script for Paper Trading System (Windows)

echo 🚀 Polymarket Paper Trading System - Quick Start
echo ==================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo Quick commands:
echo   quickstart.bat scan       - Scan for signals
echo   quickstart.bat trade      - Execute paper trades
echo   quickstart.bat report     - Generate report
echo   quickstart.bat full       - Run full cycle
echo.

REM Run based on argument
if "%~1"=="scan" (
    echo 🔍 Running market scan...
    python STRATEGY_SIGNALS.py --scan
) else if "%~1"=="trade" (
    echo 💰 Executing paper trades...
    python STRATEGY_SIGNALS.py --paper-trade
) else if "%~1"=="report" (
    echo 📊 Generating report...
    python STRATEGY_SIGNALS.py --report
) else if "%~1"=="full" (
    echo 🔄 Running full cycle...
    python STRATEGY_SIGNALS.py --run-all
) else (
    echo Usage: quickstart.bat [scan^|trade^|report^|full]
)
