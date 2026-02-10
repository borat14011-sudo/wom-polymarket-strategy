@echo off
chcp 65001 >nul
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║       KAIZEN NEXT WAVE SPAWNER - CONTROL CENTER          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo [1] View Live Dashboard
echo [2] Check Spawner Status
echo [3] View Activity Log
echo [4] List Active Agents
echo [5] Check Deliverables
echo [6] Restart Spawner
echo [7] Stop Spawner
echo [Q] Quit
echo.
set /p choice="Select option: "

if "%choice%"=="1" (
    start .kaizen_dashboard.html
    goto menu
)
if "%choice%"=="2" (
    type .kaizen_spawner_state.json
    pause
    goto menu
)
if "%choice%"=="3" (
    type .kaizen_spawner.log
    pause
    goto menu
)
if "%choice%"=="4" (
    dir /b .spawn_*.json 2>nul || echo No active agents found
    pause
    goto menu
)
if "%choice%"=="5" (
    echo Checking deliverables...
    if exist RESOLVED_DATA_FIXED.json (echo ✅ RESOLVED_DATA_FIXED.json) else (echo ⏳ RESOLVED_DATA_FIXED.json)
    if exist FEE_ADJUSTED_STRATEGIES.md (echo ✅ FEE_ADJUSTED_STRATEGIES.md) else (echo ⏳ FEE_ADJUSTED_STRATEGIES.md)
    if exist TRADEABLE_MARKETS.json (echo ✅ TRADEABLE_MARKETS.json) else (echo ⏳ TRADEABLE_MARKETS.json)
    if exist NEW_VIABLE_STRATEGIES.md (echo ✅ NEW_VIABLE_STRATEGIES.md) else (echo ⏳ NEW_VIABLE_STRATEGIES.md)
    pause
    goto menu
)
if "%choice%"=="6" (
    taskkill /F /IM python.exe 2>nul
    timeout /t 2 >nul
    start /B python kaizen_spawner.py
    echo Spawner restarted!
    timeout /t 2 >nul
    goto menu
)
if "%choice%"=="7" (
    taskkill /F /IM python.exe 2>nul
    echo Spawner stopped!
    pause
    goto menu
)
if /I "%choice%"=="Q" exit

:menu
cls
kaizen_control.bat
