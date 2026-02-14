@echo off
echo ==========================================
echo Polymarket Trading Bot Setup (Windows)
echo ==========================================

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo ==========================================
    echo IMPORTANT: Edit .env file with your credentials
    echo ==========================================
    echo.
    echo 1. Get your private key from:
    echo    https://reveal.magic.link/polymarket
    echo.
    echo 2. Get your funder address from:
    echo    polymarket.com/settings ^> Wallet
    echo.
    echo 3. Make at least one manual trade on polymarket.com
    echo    (This activates API permissions)
    echo.
    echo 4. Edit .env and add:
    echo    POLYMARKET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
    echo    POLYMARKET_FUNDER_ADDRESS=0xYOUR_ADDRESS
    echo.
    pause
)

REM Test the setup
echo Testing setup...
python test_bot.py
if errorlevel 1 (
    echo Setup test failed
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To run the bot:
echo   python main.py
echo.
echo Options:
echo   1. Run once (immediate)
echo   2. Run scheduled (every 30 minutes)
echo   3. Test components only
echo.
echo Start with option 3 to verify everything works!
echo.
pause