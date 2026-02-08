# Simplified Polymarket Historical Price Fetcher
param(
    [int]$SampleSize = 5
)

$csvPath = "polymarket_resolved_markets.csv"
$CLOB_API = "https://clob.polymarket.com"

Write-Host ""
Write-Host "================================================================================"
Write-Host "Polymarket Historical Price Fetcher"
Write-Host "================================================================================"
Write-Host ""

if (-not (Test-Path $csvPath)) {
    Write-Host "Error: CSV not found!" -ForegroundColor Red
    exit 1
}

$markets = Import-Csv $csvPath
Write-Host "Loaded $($markets.Count) markets"

# Select high-volume markets
$selected = $markets | Where-Object { 
    [double]$_.volume_usd -gt 10000 
} | Select-Object -First $SampleSize

Write-Host "Selected $($selected.Count) markets for price history fetch"
Write-Host ""

$results = @()

for ($i = 0; $i -lt $selected.Count; $i++) {
    $market = $selected[$i]
    $num = $i + 1
    
    Write-Host "[$num/$($selected.Count)] $($market.question)" -ForegroundColor Cyan
    
    if (-not $market.condition_id) {
        Write-Host "  Skipping: No condition ID" -ForegroundColor Yellow
        continue
    }
    
    # Try to fetch market info from CLOB
    $url = "$CLOB_API/markets/$($market.condition_id)"
    
    try {
        Write-Host "  Fetching from CLOB API..." -ForegroundColor Gray
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
        
        Write-Host "  ✓ Retrieved market data" -ForegroundColor Green
        
        $results += [PSCustomObject]@{
            market_id = $market.market_id
            question = $market.question
            winner = $market.winner
            volume = $market.volume_usd
            clob_data = $response
        }
    }
    catch {
        Write-Host "  Warning: API returned error (market may be archived)" -ForegroundColor Yellow
    }
    
    Start-Sleep -Milliseconds 500
    Write-Host ""
}

Write-Host ""
Write-Host "================================================================================"
Write-Host "Fetch Complete" -ForegroundColor Green
Write-Host "================================================================================"
Write-Host ""
Write-Host "Successfully fetched data for $($results.Count) markets"

if ($results.Count -gt 0) {
    $outPath = "polymarket_clob_data.json"
    $results | ConvertTo-Json -Depth 10 | Out-File -FilePath $outPath -Encoding UTF8
    Write-Host "Saved to: $outPath" -ForegroundColor Green
}

Write-Host ""
