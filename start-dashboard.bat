@echo off
REM Dashboard Launcher Script for Windows
REM Starts Flask API backend and opens dashboard in browser

echo ================================================
echo    Trading System Dashboard Launcher
echo ================================================
echo.

REM Check if database exists
if not exist "polymarket_data.db" (
    echo [WARNING] Database not found!
    echo.
    echo Expected file: polymarket_data.db
    echo.
    echo Run the data collectors first:
    echo   python polymarket-data-collector.py
    echo   python twitter-hype-monitor.py
    echo.
    echo The dashboard will still start, but will show no data.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b
    echo.
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Flask not found. Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo [OK] All dependencies found
echo.

REM Start Flask API in background
echo [INFO] Starting Flask API server...
start /b python api.py
timeout /t 2 /nobreak >nul

echo [OK] API server running on http://localhost:5000
echo.

REM Open dashboard in browser
echo [INFO] Opening dashboard in browser...
start "" "%CD%\dashboard.html"

echo.
echo ================================================
echo    Dashboard is running!
echo ================================================
echo    Dashboard: file:///%CD%/dashboard.html
echo    API:       http://localhost:5000
echo ================================================
echo.
echo Dashboard will auto-refresh every 60 seconds
echo.
echo Press Ctrl+C to stop the server
echo.

pause
