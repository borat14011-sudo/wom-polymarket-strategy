# PowerShell Script to Setup Windows Task Scheduler for Historical Price Scraper
# Run as Administrator: Right-click PowerShell > Run as Administrator
# Then execute: .\setup_scraper_task.ps1

$TaskName = "PolymarketHistoricalScraper"
$ScriptPath = Join-Path $PSScriptRoot "historical_scraper.py"
$PythonPath = (Get-Command python).Source
$WorkingDir = $PSScriptRoot

Write-Host "Setting up Windows Task Scheduler job..." -ForegroundColor Cyan
Write-Host "Task Name: $TaskName" -ForegroundColor Yellow
Write-Host "Script: $ScriptPath" -ForegroundColor Yellow
Write-Host "Python: $PythonPath" -ForegroundColor Yellow

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "⚠️  Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create trigger (every hour)
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)

# Create action (run Python script)
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $WorkingDir

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -Description "Scrapes Polymarket top 100 markets every hour to build historical price database" `
    -RunLevel Highest

Write-Host "✅ Task registered successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To verify:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskName $TaskName | Format-List" -ForegroundColor Gray
Write-Host ""
Write-Host "To run manually:" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName $TaskName" -ForegroundColor Gray
Write-Host ""
Write-Host "To disable:" -ForegroundColor Cyan
Write-Host "  Disable-ScheduledTask -TaskName $TaskName" -ForegroundColor Gray
Write-Host ""
Write-Host "To remove:" -ForegroundColor Cyan
Write-Host "  Unregister-ScheduledTask -TaskName $TaskName -Confirm:`$false" -ForegroundColor Gray
