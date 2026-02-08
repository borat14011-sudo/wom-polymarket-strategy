# Simple NO-Side Backtest Analysis
# Using PowerShell to avoid Node.js memory issues

$csv = Import-Csv -Path "polymarket_resolved_markets.csv"

Write-Host "NO-SIDE BIAS BACKTEST - SIMPLIFIED ANALYSIS" -ForegroundColor Green
Write-Host "=" * 80

# Filter for NO-side winning markets (YES < 15% final price)
$no_winners = $csv | Where-Object {
    $prices = $_.final_prices -split '\|'
    $yes_price = [double]$prices[0]
    $volume = [double]$_.volume_usd
    $yes_price -lt 0.15 -and $volume -gt 1000
}

Write-Host "`nFiltered Markets:"
Write-Host "  Total resolved markets: $($csv.Count)"
Write-Host "  Markets with YES < 15%: $($no_winners.Count)"
Write-Host "  (These are potential NO-side wins)"

# Calculate statistics
$total_volume = ($no_winners | Measure-Object -Property volume_usd -Sum).Sum
$avg_volume = $total_volume / $no_winners.Count

Write-Host "`nVolume Statistics:"
Write-Host "  Total volume: `$$([math]::Round($total_volume, 0))"
Write-Host "  Average volume per market: `$$([math]::Round($avg_volume, 0))"

# Sample trades
Write-Host "`nSample Markets (First 20):"
Write-Host "-" * 80

$sample = $no_winners | Select-Object -First 20
$trade_log = @()

foreach ($market in $sample) {
    $prices = $market.final_prices -split '\|'
    $yes_final = [double]$prices[0]
    $no_final = [double]$prices[1]
    
    # Assume entry when YES was around 10-12% (conservative)
    $entry_yes = 0.12
    $entry_no = 0.88
    
    # Calculate P&L (NO side)
    $pnl = ($no_final - $entry_no) / $entry_no
    
    $trade_log += [PSCustomObject]@{
        Question = $market.question
        Winner = $market.winner
        Entry_NO = $entry_no
        Exit_NO = $no_final
        PnL = $pnl
        Volume = [double]$market.volume_usd
    }
    
    $pnl_pct = [math]::Round($pnl * 100, 1)
    $result = if ($market.winner -eq "No") { "WIN" } else { "LOSS" }
    Write-Host "  $result - $($market.question.Substring(0, 60))... | P&L: $pnl_pct%"
}

# Calculate metrics
$wins = $trade_log | Where-Object { $_.Winner -eq "No" }
$losses = $trade_log | Where-Object { $_.Winner -ne "No" }

$win_rate = $wins.Count / $trade_log.Count
$avg_pnl = ($trade_log | Measure-Object -Property PnL -Average).Average

Write-Host "`n" + "=" * 80
Write-Host "PERFORMANCE METRICS" -ForegroundColor Yellow
Write-Host "=" * 80

Write-Host "`nWin/Loss:"
Write-Host "  Total Trades: $($trade_log.Count)"
Write-Host "  Wins: $($wins.Count)"
Write-Host "  Losses: $($losses.Count)"
Write-Host "  Win Rate: $([math]::Round($win_rate * 100, 1))%"

Write-Host "`nReturns:"
Write-Host "  Average P&L per trade: $([math]::Round($avg_pnl * 100, 1))%"

if ($wins.Count -gt 0) {
    $avg_win = ($wins | Measure-Object -Property PnL -Average).Average
    Write-Host "  Average Win: +$([math]::Round($avg_win * 100, 1))%"
}

if ($losses.Count -gt 0) {
    $avg_loss = ($losses | Measure-Object -Property PnL -Average).Average
    Write-Host "  Average Loss: $([math]::Round($avg_loss * 100, 1))%"
}

# Export to CSV
$trade_log | Export-Csv -Path "trades_no_side.csv" -NoTypeInformation

Write-Host "`n" + "=" * 80
Write-Host "Exported trade log to: trades_no_side.csv" -ForegroundColor Green
Write-Host "=" * 80
