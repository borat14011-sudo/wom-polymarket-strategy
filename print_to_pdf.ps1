# PowerShell script to print HTML to PDF
$htmlPath = "C:\Users\Borat\.openclaw\workspace\Polymarket_Investment_Presentation.html"
$pdfPath = "C:\Users\Borat\OneDrive\Trading\Polymarket_Investment_Presentation.pdf"

# Create OneDrive Trading directory if it doesn't exist
$onedrivePath = "C:\Users\Borat\OneDrive\Trading"
if (-not (Test-Path $onedrivePath)) {
    New-Item -ItemType Directory -Path $onedrivePath -Force
    Write-Host "Created directory: $onedrivePath"
}

Write-Host "========================================"
Write-Host "PRINT HTML TO PDF"
Write-Host "========================================"
Write-Host "HTML File: $htmlPath"
Write-Host "PDF Destination: $pdfPath"
Write-Host ""

# Check if files exist
if (-not (Test-Path $htmlPath)) {
    Write-Host "ERROR: HTML file not found: $htmlPath" -ForegroundColor Red
    exit 1
}

Write-Host "Opening HTML file in default browser..."
Start-Process $htmlPath

Write-Host ""
Write-Host "INSTRUCTIONS TO SAVE AS PDF:"
Write-Host "1. Browser will open with the presentation"
Write-Host "2. Click the 'Print/Save as PDF' button (top-right)"
Write-Host "3. OR Press Ctrl+P"
Write-Host "4. Select 'Save as PDF' as destination"
Write-Host "5. Save to: $pdfPath"
Write-Host "6. Click Save"
Write-Host ""
Write-Host "The PDF will be saved to your OneDrive Trading folder."
Write-Host "========================================"