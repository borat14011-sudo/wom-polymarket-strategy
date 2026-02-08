# PowerShell script to run Python backtest
$pythonPath = "C:\Users\Borat\AppData\Local\Microsoft\WindowsApps\python.exe"

if (Test-Path $pythonPath) {
    & $pythonPath backtest_time_horizon.py
} else {
    Write-Host "Python not found. Trying system python..."
    python backtest_time_horizon.py
}
