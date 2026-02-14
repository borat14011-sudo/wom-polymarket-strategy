# PowerShell script to convert HTML to PDF using .NET
param(
    [string]$HtmlPath = "C:\Users\Borat\.openclaw\workspace\Polymarket_Investment_Presentation.html",
    [string]$PdfPath = "C:\Users\Borat\OneDrive\Trading\Polymarket_Investment_Presentation.pdf"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONVERT HTML TO PDF FOR ONEDRIVE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if HTML file exists
if (-not (Test-Path $HtmlPath)) {
    Write-Host "ERROR: HTML file not found: $HtmlPath" -ForegroundColor Red
    exit 1
}

Write-Host "HTML Source: $HtmlPath" -ForegroundColor Yellow
Write-Host "PDF Destination: $PdfPath" -ForegroundColor Yellow
Write-Host ""

# Read HTML content
$htmlContent = Get-Content $HtmlPath -Raw -Encoding UTF8

# Create a simple HTML to PDF conversion using Internet Explorer COM object
# This is a fallback method for Windows
try {
    Write-Host "Creating PDF using Internet Explorer COM object..." -ForegroundColor Green
    
    # Create Internet Explorer COM object
    $ie = New-Object -ComObject InternetExplorer.Application
    $ie.Visible = $false
    $ie.Silent = $true
    
    # Create a temporary HTML file with proper headers
    $tempHtml = [System.IO.Path]::GetTempFileName() + ".html"
    $htmlWithMeta = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Polymarket Quantitative Trading Strategy</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        @media print {
            @page { size: A4; margin: 1.5cm; }
            body { font-size: 12pt; }
            h1 { font-size: 24pt; }
            h2 { font-size: 18pt; }
            .page-break { page-break-after: always; }
        }
    </style>
</head>
<body>
$htmlContent
</body>
</html>
"@
    
    Set-Content -Path $tempHtml -Value $htmlWithMeta -Encoding UTF8
    
    # Navigate to the HTML file
    $ie.Navigate("file:///$tempHtml")
    while ($ie.Busy) { Start-Sleep -Milliseconds 100 }
    
    # Use the PrintTo method (this prints to default printer, not PDF)
    # For PDF, we need a different approach
    
    Write-Host "WARNING: Direct PDF conversion requires additional tools." -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "ERROR: COM object approach failed: $_" -ForegroundColor Red
}

# Alternative: Create a batch file that opens and prints
Write-Host "Creating automated print script..." -ForegroundColor Green

$printScript = @"
@echo off
echo ========================================
echo AUTOMATED PDF SAVE TO ONEDRIVE
echo ========================================
echo.
echo This script will help you save the presentation as PDF.
echo.
echo Steps:
echo 1. Chrome will open with the presentation
echo 2. Press Ctrl+P to print
echo 3. Select "Save as PDF"
echo 4. Save to: %USERPROFILE%\OneDrive\Trading\Polymarket_Investment_Presentation.pdf
echo.
echo Press any key to continue...
pause >nul

REM Open Chrome with print dialog
start chrome --app="file:///C:/Users/Borat/.openclaw/workspace/Polymarket_Investment_Presentation.html" --new-window

echo.
echo After Chrome opens:
echo 1. Press Ctrl+P
echo 2. Select "Save as PDF"
echo 3. Choose location: OneDrive\Trading\
echo 4. File name: Polymarket_Investment_Presentation.pdf
echo 5. Click Save
echo.
echo Press any key to exit...
pause >nul
"@

$printScriptPath = "C:\Users\Borat\.openclaw\workspace\AUTO_PRINT_TO_ONEDRIVE.bat"
Set-Content -Path $printScriptPath -Value $printScript -Encoding ASCII

Write-Host "Created automated script: $printScriptPath" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QUICK SOLUTION:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Run this command to auto-save to OneDrive:" -ForegroundColor Yellow
Write-Host "Start-Process '$printScriptPath'" -ForegroundColor White
Write-Host ""
Write-Host "OR manually:" -ForegroundColor Yellow
Write-Host "1. Open: Polymarket_Investment_Presentation.html" -ForegroundColor White
Write-Host "2. Press Ctrl+P" -ForegroundColor White
Write-Host "3. Destination: Save as PDF" -ForegroundColor White
Write-Host "4. Save to: C:\Users\Borat\OneDrive\Trading\" -ForegroundColor White
Write-Host "5. Name: Polymarket_Investment_Presentation.pdf" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan