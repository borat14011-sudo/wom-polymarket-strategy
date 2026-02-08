# Polymarket Data Analysis Script
# Analyzes the scraped resolved market data

$csvPath = "polymarket_resolved_markets.csv"

if (-not (Test-Path $csvPath)) {
    Write-Host "Error: $csvPath not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "POLYMARKET RESOLVED MARKETS - DATA ANALYSIS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Load data
$data = Import-Csv $csvPath

Write-Host "DATASET OVERVIEW" -ForegroundColor Yellow
Write-Host "-" * 80
Write-Host "Total markets collected: $($data.Count)"
Write-Host ""

# Winner statistics
$withWinners = ($data | Where-Object { $_.winner -and $_.winner -ne "" }).Count
$withoutWinners = $data.Count - $withWinners
Write-Host "Markets with determined winners: $withWinners ($([math]::Round(100.0*$withWinners/$data.Count, 1))%)"
Write-Host "Markets without determined winners: $withoutWinners"
Write-Host ""

# Volume statistics
$withVolume = ($data | Where-Object { [double]$_.volume_usd -gt 0 }).Count
Write-Host "Markets with volume data: $withVolume ($([math]::Round(100.0*$withVolume/$data.Count, 1))%)"
Write-Host ""

# Calculate total volume
$totalVolume = ($data | ForEach-Object { [double]$_.volume_usd } | Measure-Object -Sum).Sum
Write-Host "Total trading volume: `$$([math]::Round($totalVolume, 2).ToString('N2'))"
Write-Host "Average volume per market: `$$([math]::Round($totalVolume/$data.Count, 2).ToString('N2'))"
Write-Host ""

# Volume distribution
$highVolume = ($data | Where-Object { [double]$_.volume_usd -gt 100000 }).Count
$medVolume = ($data | Where-Object { [double]$_.volume_usd -gt 10000 -and [double]$_.volume_usd -le 100000 }).Count
$lowVolume = ($data | Where-Object { [double]$_.volume_usd -gt 0 -and [double]$_.volume_usd -le 10000 }).Count
$noVolume = ($data | Where-Object { [double]$_.volume_usd -eq 0 }).Count

Write-Host "VOLUME DISTRIBUTION" -ForegroundColor Yellow
Write-Host "-" * 80
Write-Host "High volume (>$100k): $highVolume markets"
Write-Host "Medium volume ($10k-$100k): $medVolume markets"
Write-Host "Low volume ($0-$10k): $lowVolume markets"
Write-Host "No volume data: $noVolume markets"
Write-Host ""

# Outcome analysis
Write-Host "OUTCOME ANALYSIS" -ForegroundColor Yellow
Write-Host "-" * 80

# Count YES vs NO winners (for binary markets)
$yesWinners = ($data | Where-Object { $_.winner -eq "Yes" }).Count
$noWinners = ($data | Where-Object { $_.winner -eq "No" }).Count
$otherWinners = ($data | Where-Object { $_.winner -and $_.winner -ne "Yes" -and $_.winner -ne "No" }).Count

Write-Host "Binary YES/NO markets:"
Write-Host "  YES winners: $yesWinners ($([math]::Round(100.0*$yesWinners/($yesWinners+$noWinners), 1))%)"
Write-Host "  NO winners: $noWinners ($([math]::Round(100.0*$noWinners/($yesWinners+$noWinners), 1))%)"
Write-Host "Multi-outcome market winners: $otherWinners"
Write-Host ""

# Event analysis
$uniqueEvents = ($data | Select-Object -Unique event_id).Count
Write-Host "EVENTS" -ForegroundColor Yellow
Write-Host "-" * 80
Write-Host "Unique events: $uniqueEvents"
Write-Host "Average markets per event: $([math]::Round($data.Count / $uniqueEvents, 2))"
Write-Host ""

# Top markets by volume
Write-Host "TOP 10 MARKETS BY VOLUME" -ForegroundColor Yellow
Write-Host "-" * 80
$topMarkets = $data | Sort-Object { [double]$_.volume_usd } -Descending | Select-Object -First 10

$i = 1
foreach ($market in $topMarkets) {
    $question = $market.question
    if ($question.Length -gt 60) {
        $question = $question.Substring(0, 60) + "..."
    }
    $volume = [math]::Round([double]$market.volume_usd, 2)
    Write-Host "$i. $question"
    Write-Host "   Winner: $($market.winner) | Volume: `$$($volume.ToString('N2'))"
    $i++
}
Write-Host ""

# Date range analysis
Write-Host "DATE RANGE" -ForegroundColor Yellow
Write-Host "-" * 80
$datesWithData = $data | Where-Object { $_.event_end_date -and $_.event_end_date -ne "" }
if ($datesWithData.Count -gt 0) {
    $dates = $datesWithData | ForEach-Object { [DateTime]::Parse($_.event_end_date) }
    $minDate = ($dates | Measure-Object -Minimum).Minimum
    $maxDate = ($dates | Measure-Object -Maximum).Maximum
    Write-Host "Earliest event end date: $($minDate.ToString('yyyy-MM-dd'))"
    Write-Host "Latest event end date: $($maxDate.ToString('yyyy-MM-dd'))"
    Write-Host "Date range: $([math]::Round(($maxDate - $minDate).TotalDays, 0)) days"
}
else {
    Write-Host "No date data available"
}
Write-Host ""

# Sample markets
Write-Host "SAMPLE MARKETS WITH COMPLETE DATA" -ForegroundColor Yellow
Write-Host "-" * 80
$sampleMarkets = $data | Where-Object { 
    $_.winner -and 
    [double]$_.volume_usd -gt 0 -and 
    $_.outcomes -and 
    $_.final_prices 
} | Select-Object -First 5

$i = 1
foreach ($market in $sampleMarkets) {
    Write-Host ""
    Write-Host "$i. Event: $($market.event_title)" -ForegroundColor Cyan
    Write-Host "   Question: $($market.question)"
    Write-Host "   Outcomes: $($market.outcomes)"
    Write-Host "   Final Prices: $($market.final_prices)"
    Write-Host "   Winner: $($market.winner)"
    Write-Host "   Volume: `$$([math]::Round([double]$market.volume_usd, 2).ToString('N2'))"
    Write-Host "   End Date: $($market.event_end_date)"
    $i++
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Analysis complete!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Files available:" -ForegroundColor Yellow
Write-Host "  - polymarket_resolved_markets.csv (spreadsheet format)"
Write-Host "  - polymarket_resolved_markets.json (programming format)"
Write-Host ""
Write-Host "Data is ready for backtesting!" -ForegroundColor Green
Write-Host ""
