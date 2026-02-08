"""
Windows Task Scheduler Setup for Iran Position Monitor
Creates scheduled task to run api_monitor.py every 15 minutes

Usage:
    Run PowerShell as Administrator, then:
    .\setup_iran_monitor_task.ps1
"""

# Configuration
$TaskName = "PolymarketIranMonitor"
$ScriptPath = $PSScriptRoot + "\api_monitor.py"
$PythonPath = (Get-Command python).Path  # Auto-detect Python

# Task settings
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration ([TimeSpan]::MaxValue)
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $PSScriptRoot
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries

# Create the task
Write-Host "[INFO] Creating scheduled task: $TaskName"
Write-Host "[INFO] Python: $PythonPath"
Write-Host "[INFO] Script: $ScriptPath"
Write-Host "[INFO] Interval: Every 15 minutes"

try {
    Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -Force
    
    Write-Host "[SUCCESS] Scheduled task created successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Open Task Scheduler (taskschd.msc)"
    Write-Host "2. Find task: $TaskName"
    Write-Host "3. Right-click > Run to test immediately"
    Write-Host "4. Check logs: logs\api_monitor.log"
    Write-Host ""
    Write-Host "To remove the task:"
    Write-Host "    Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
    
} catch {
    Write-Host "[ERROR] Failed to create scheduled task: $_"
    Write-Host ""
    Write-Host "Make sure you're running PowerShell as Administrator!"
    exit 1
}
