# Polymarket Historical Price Fetcher
# Fetches historical price snapshots for markets using CLOB API

param(
    [int]$SampleSize = 10,  # Number of markets to fetch history for
    [int]$DelayMs = 500     # Delay between requests to avoid rate limiting
)

$ErrorActionPreference = "Continue"

$csvPath = "polymarket_resolved_markets.csv"
$outputPath = "polymarket_price_history.json"
$CLOB_API = "https://clob.polymarket.com"

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Polymarket Historical Price Fetcher" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $csvPath)) {
    Write-Host "Error: $csvPath not found! Run the scraper first." -ForegroundColor Red
    exit 1
}

# Load market data
$markets = Import-Csv $csvPath

Write-Host "Loaded $($markets.Count) markets from CSV"
Write-Host "Will fetch historical data for $SampleSize markets"
Write-Host ""

# Select markets with volume and token IDs
$marketsToFetch = $markets | Where-Object { 
    [double]$_.volume_usd -gt 10000 -and 
    $_.clob_token_ids -and 
    $_.clob_token_ids -ne "" 
} | Select-Object -First $SampleSize

Write-Host "Selected $($marketsToFetch.Count) high-volume markets for price history"
Write-Host ""

$priceHistory = @()

function Get-TokenPriceHistory {
    param(
        [string]$tokenId,
        [string]$marketId
    )
    
    # Try to get trades for this token
    $url = "$CLOB_API/trades?token_id=$tokenId"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
        return $response
    }
    catch {
        $tokenPreview = if ($tokenId.Length -gt 20) { $tokenId.Substring(0, 20) + "..." } else { $tokenId }
        Write-Host "  Warning: Could not fetch trades for token $tokenPreview" -ForegroundColor Yellow
        return @()
    }
}

function Get-MarketPriceSnapshot {
    param(
        [string]$conditionId
    )
    
    # Try to get current orderbook
    $url = "$CLOB_API/markets/$conditionId"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
        return $response
    }
    catch {
        Write-Host "  Warning: Could not fetch market data" -ForegroundColor Yellow
        return $null
    }
}

$i = 1
foreach ($market in $marketsToFetch) {
    $questionPreview = if ($market.question.Length -gt 60) { $market.question.Substring(0, 60) } else { $market.question }
    Write-Host "[$i/$($marketsToFetch.Count)] Processing: $questionPreview..." -ForegroundColor Cyan
    
    # Parse token IDs
    $tokenIds = $market.clob_token_ids -split '\|' | Where-Object { $_ -and $_ -ne "" }
    
    if ($tokenIds.Count -eq 0) {
        Write-Host "  Skipping: No token IDs available" -ForegroundColor Yellow
        $i++
        continue
    }
    
    # Clean token IDs (remove brackets and quotes)
    $tokenIds = $tokenIds | ForEach-Object { 
        $_ -replace '[\[\]"\s]', ''
    }
    
    Write-Host "  Found $($tokenIds.Count) token ID(s)"
    
    $marketHistory = [PSCustomObject]@{
        market_id = $market.market_id
        condition_id = $market.condition_id
        question = $market.question
        event_title = $market.event_title
        winner = $market.winner
        outcomes = $market.outcomes
        final_prices = $market.final_prices
        volume_usd = $market.volume_usd
        tokens = @()
    }
    
    # Fetch trades for each token (YES/NO)
    $tokenIdx = 0
    $outcomes = $market.outcomes -split '\|'
    
    foreach ($tokenId in $tokenIds) {
        if ($tokenIdx -lt $outcomes.Count) {
            $outcome = $outcomes[$tokenIdx]
        }
        else {
            $outcome = "Token$tokenIdx"
        }
        
        Write-Host "  Fetching trades for $outcome token..." -ForegroundColor Gray
        
        $trades = Get-TokenPriceHistory -tokenId $tokenId -marketId $market.market_id
        
        if ($trades -and $trades.Count -gt 0) {
            Write-Host "    → Found $($trades.Count) trades" -ForegroundColor Green
            
            # Store trades with timestamps
            $tokenData = [PSCustomObject]@{
                outcome = $outcome
                token_id = $tokenId
                trade_count = $trades.Count
                trades = $trades | Select-Object -First 100 | ForEach-Object {
                    [PSCustomObject]@{
                        timestamp = $_.timestamp
                        price = $_.price
                        size = $_.size
                        side = $_.side
                    }
                }
            }
            
            $marketHistory.tokens += $tokenData
        }
        else {
            Write-Host "    → No trades found" -ForegroundColor Yellow
        }
        
        $tokenIdx++
        Start-Sleep -Milliseconds $DelayMs
    }
    
    if ($marketHistory.tokens.Count -gt 0) {
        $priceHistory += $marketHistory
        Write-Host "  ✓ Added to history dataset" -ForegroundColor Green
    }
    
    $i++
    Write-Host ""
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Price History Collection Complete" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Markets with price history: $($priceHistory.Count)"

if ($priceHistory.Count -gt 0) {
    $totalTrades = ($priceHistory.tokens.trade_count | Measure-Object -Sum).Sum
    Write-Host "Total historical trades collected: $totalTrades"
    Write-Host ""
    
    # Save to JSON
    Write-Host "Saving to $outputPath..." -ForegroundColor Cyan
    $priceHistory | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputPath -Encoding UTF8
    Write-Host "✓ Price history saved!" -ForegroundColor Green
    
    # Show sample
    Write-Host ""
    Write-Host "SAMPLE: First market with price history" -ForegroundColor Yellow
    Write-Host "-" * 80
    $sample = $priceHistory[0]
    Write-Host "Question: $($sample.question)"
    Write-Host "Winner: $($sample.winner)"
    Write-Host "Outcomes: $($sample.outcomes)"
    Write-Host ""
    foreach ($token in $sample.tokens) {
        Write-Host "  $($token.outcome): $($token.trade_count) trades"
        if ($token.trades.Count -gt 0) {
            $firstTrade = $token.trades[0]
            $lastTrade = $token.trades[-1]
            Write-Host "    First trade: Price=$($firstTrade.price) at $($firstTrade.timestamp)"
            Write-Host "    Last trade: Price=$($lastTrade.price) at $($lastTrade.timestamp)"
        }
    }
}
else {
    Write-Host "No price history could be fetched. Markets may be too old or API structure changed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Complete! You now have:" -ForegroundColor Green
Write-Host "  1. polymarket_resolved_markets.csv - Resolved market outcomes"
Write-Host "  2. polymarket_resolved_markets.json - Same data in JSON format"
Write-Host "  3. polymarket_price_history.json - Historical price snapshots"
Write-Host ""
Write-Host "This data is ready for REAL backtesting!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
