# Polymarket Historical Data Scraper (PowerShell)
# Collects real historical data from resolved markets

$ErrorActionPreference = "Continue"

$GAMMA_API = "https://gamma-api.polymarket.com"
$allMarketsData = @()

Write-Host "=" * 80
Write-Host "Polymarket Resolved Markets Scraper"
Write-Host "=" * 80
Write-Host ""

function Get-ResolvedEvents {
    param(
        [int]$limit = 100,
        [int]$offset = 0
    )
    
    $url = "$GAMMA_API/events?closed=true&limit=$limit&offset=$offset&order=id&ascending=false"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
        return $response
    }
    catch {
        Write-Host "Error fetching events at offset $offset : $_" -ForegroundColor Red
        return @()
    }
}

function Parse-JsonString {
    param([string]$jsonStr)
    
    if ([string]::IsNullOrEmpty($jsonStr)) {
        return @()
    }
    
    try {
        return $jsonStr | ConvertFrom-Json
    }
    catch {
        return @()
    }
}

function Get-Winner {
    param($market)
    
    # Check for explicit winner field
    if ($market.winner) {
        return $market.winner
    }
    
    if ($market.resolvedOutcome) {
        return $market.resolvedOutcome
    }
    
    # Parse outcomes and prices
    $outcomes = Parse-JsonString $market.outcomes
    $prices = Parse-JsonString $market.outcomePrices
    
    if ($outcomes.Count -eq 0 -or $prices.Count -eq 0 -or $outcomes.Count -ne $prices.Count) {
        return $null
    }
    
    # Find outcome with highest price (closest to 1.00)
    $maxPrice = 0
    $maxIdx = 0
    
    for ($i = 0; $i -lt $prices.Count; $i++) {
        $price = [double]$prices[$i]
        if ($price -gt $maxPrice) {
            $maxPrice = $price
            $maxIdx = $i
        }
    }
    
    # If price is >= 0.95, it's likely the winner
    if ($maxPrice -ge 0.95) {
        return $outcomes[$maxIdx]
    }
    
    return $null
}

function Extract-MarketData {
    param($event)
    
    $marketsData = @()
    
    $eventId = $event.id
    $eventTitle = $event.title
    $eventSlug = $event.slug
    $eventDescription = $event.description
    $eventEndDate = $event.endDate
    $eventClosed = $event.closed
    
    foreach ($market in $event.markets) {
        $marketId = $market.id
        $conditionId = $market.conditionId
        $question = if ($market.question) { $market.question } else { $eventTitle }
        
        # Parse outcomes and prices
        $outcomes = Parse-JsonString $market.outcomes
        $finalPrices = Parse-JsonString $market.outcomePrices
        
        # Determine winner
        $winner = Get-Winner $market
        
        # Get token IDs
        $clobTokenIds = if ($market.clobTokenIds) { $market.clobTokenIds } else { @() }
        
        # Volume data
        $volumeUsd = if ($market.volume) { $market.volume } else { 0 }
        $volumeNum = if ($market.volumeNum) { $market.volumeNum } else { 0 }
        
        $marketData = [PSCustomObject]@{
            event_id = $eventId
            event_title = $eventTitle
            event_slug = $eventSlug
            event_end_date = $eventEndDate
            market_id = $marketId
            condition_id = $conditionId
            question = $question
            outcomes = ($outcomes -join "|")
            final_prices = ($finalPrices -join "|")
            winner = $winner
            closed = $eventClosed
            volume_usd = $volumeUsd
            volume_num = $volumeNum
            clob_token_ids = ($clobTokenIds -join "|")
            description = if ($eventDescription) { $eventDescription.Substring(0, [Math]::Min(200, $eventDescription.Length)) } else { "" }
            created_time = (Get-Date -Format "o")
        }
        
        $marketsData += $marketData
    }
    
    return $marketsData
}

# Main scraping logic
Write-Host "Starting scrape for 100+ resolved markets..."
Write-Host ""

$offset = 0
$limit = 100
$totalMarkets = 0
$requestCount = 0
$targetCount = 100
$maxRequests = 20

while ($totalMarkets -lt $targetCount -and $requestCount -lt $maxRequests) {
    Write-Host "Fetching events: offset=$offset, limit=$limit" -ForegroundColor Cyan
    
    $events = Get-ResolvedEvents -limit $limit -offset $offset
    
    if ($events.Count -eq 0) {
        Write-Host "No more events found." -ForegroundColor Yellow
        break
    }
    
    Write-Host "Retrieved $($events.Count) events" -ForegroundColor Green
    
    $eventNum = 0
    foreach ($event in $events) {
        $eventNum++
        $eventTitle = $event.title
        if ($eventTitle.Length -gt 60) {
            $eventTitle = $eventTitle.Substring(0, 60) + "..."
        }
        
        Write-Host "  [$eventNum/$($events.Count)] Processing: $eventTitle (ID: $($event.id))"
        
        # Extract market data
        $markets = Extract-MarketData $event
        
        if ($markets.Count -gt 0) {
            $allMarketsData += $markets
            $totalMarkets += $markets.Count
            Write-Host "    → Extracted $($markets.Count) market(s). Total: $totalMarkets" -ForegroundColor Green
        }
        
        Start-Sleep -Milliseconds 100
    }
    
    $offset += $limit
    $requestCount++
    
    if ($events.Count -eq $limit) {
        Write-Host ""
        Write-Host "Pausing before next batch..." -ForegroundColor Yellow
        Start-Sleep -Seconds 1
    }
    else {
        Write-Host ""
        Write-Host "Received fewer events than limit - likely reached the end." -ForegroundColor Yellow
        break
    }
}

Write-Host ""
Write-Host "=" * 80
Write-Host "Scraping complete! Collected $totalMarkets markets" -ForegroundColor Green
Write-Host "=" * 80

# Print summary
Write-Host ""
Write-Host "DATA SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80
Write-Host "Total markets collected: $($allMarketsData.Count)"

$withWinners = ($allMarketsData | Where-Object { $_.winner }).Count
Write-Host "Markets with determined winners: $withWinners"

$withVolume = ($allMarketsData | Where-Object { [double]$_.volume_usd -gt 0 }).Count
Write-Host "Markets with volume data: $withVolume"

Write-Host ""
Write-Host "Sample of collected markets:" -ForegroundColor Cyan
$sampleCount = [Math]::Min(5, $allMarketsData.Count)
for ($i = 0; $i -lt $sampleCount; $i++) {
    $market = $allMarketsData[$i]
    $questionPreview = if ($market.question.Length -gt 70) { $market.question.Substring(0, 70) + "..." } else { $market.question }
    
    Write-Host ""
    Write-Host "$($i + 1). $questionPreview"
    Write-Host "   Winner: $($market.winner)"
    Write-Host "   Outcomes: $($market.outcomes)"
    Write-Host "   Final Prices: $($market.final_prices)"
    Write-Host "   Volume: `$$($market.volume_usd)"
}

# Save to CSV
Write-Host ""
Write-Host "Saving to CSV..." -ForegroundColor Cyan
$csvPath = "polymarket_resolved_markets.csv"
$allMarketsData | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "✓ Data saved to $csvPath" -ForegroundColor Green

# Save to JSON
Write-Host "Saving to JSON..." -ForegroundColor Cyan
$jsonPath = "polymarket_resolved_markets.json"
$allMarketsData | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8
Write-Host "✓ Data saved to $jsonPath" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 80
Write-Host "Scraping complete! Files saved:" -ForegroundColor Green
Write-Host "  - $csvPath"
Write-Host "  - $jsonPath"
Write-Host "=" * 80
