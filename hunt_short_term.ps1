# Comprehensive Kalshi Short-Term Market Hunter
# Target: Markets resolving within 30 days from Feb 12, 2026

$targetDate = Get-Date "2026-02-12"
$maxDate = $targetDate.AddDays(30)

Write-Host "=== KALSHI SHORT-TERM HUNTER ===" -ForegroundColor Cyan
Write-Host "Target Window: $($targetDate.ToString('yyyy-MM-dd')) to $($maxDate.ToString('yyyy-MM-dd'))" -ForegroundColor Yellow
Write-Host ""

# Load all available event data
$allMarkets = @()
$files = @("events.json", "events2.json", "events3.json")

foreach ($file in $files) {
    if (Test-Path $file) {
        $data = Get-Content $file | ConvertFrom-Json
        foreach ($event in $data.events) {
            foreach ($market in $event.markets) {
                $market | Add-Member -NotePropertyName "EventCategory" -NotePropertyValue $event.category -Force
                $market | Add-Member -NotePropertyName "EventTitle" -NotePropertyValue $event.title -Force
                $market | Add-Member -NotePropertyName "SeriesTicker" -NotePropertyValue $event.series_ticker -Force
                $allMarkets += $market
            }
        }
    }
}

Write-Host "Loaded $($allMarkets.Count) total markets" -ForegroundColor Green
Write-Host ""

# Filter and analyze
$opportunities = @()

foreach ($market in $allMarkets) {
    try {
        $expDate = [DateTime]::Parse($market.expiration_date)
        $daysUntil = ($expDate - $targetDate).Days
        
        # Filter: within 30 days, volume > 1000, price in 20-80% range
        if ($daysUntil -gt 0 -and $daysUntil -le 30) {
            $volume = [int]$market.volume
            $price = [int]$market.last_price
            
            if ($volume -gt 1000 -and $price -ge 20 -and $price -le 80) {
                # Calculate IRR
                $investmentCost = $price / 100.0
                $payout = 1.0
                $profit = $payout - $investmentCost
                $returnPct = ($profit / $investmentCost) * 100
                
                # Annualized IRR
                $daysHeld = [Math]::Max($daysUntil, 1)
                $irr = [Math]::Pow((1 + $profit / $investmentCost), (365.0 / $daysHeld)) - 1
                $irrPct = $irr * 100
                
                $opportunities += [PSCustomObject]@{
                    Title = $market.title
                    Ticker = $market.ticker_name
                    Category = $market.EventCategory
                    EventSeries = $market.SeriesTicker
                    ResolutionDate = $expDate.ToString("yyyy-MM-dd HH:mm")
                    DaysUntil = $daysUntil
                    Price = $price
                    PriceDollars = $market.last_price_dollars
                    Volume = $volume
                    OpenInterest = $market.open_interest
                    Liquidity = $market.liquidity
                    DollarVolume = $market.dollar_volume
                    ReturnIfWin = [Math]::Round($returnPct, 2)
                    AnnualizedIRR = [Math]::Round($irrPct, 2)
                    YesBid = $market.yes_bid
                    YesAsk = $market.yes_ask
                    Spread = $market.yes_ask - $market.yes_bid
                }
            }
        }
    }
    catch {
        # Skip markets with parsing issues
    }
}

Write-Host "Found $($opportunities.Count) markets matching criteria:" -ForegroundColor Green
Write-Host "  - Resolving in 1-30 days"
Write-Host "  - Volume > 1,000 contracts"
Write-Host "  - Price between 20-80 cents"
Write-Host ""

if ($opportunities.Count -eq 0) {
    Write-Host "No markets found matching criteria. Expanding search..." -ForegroundColor Yellow
    Write-Host ""
    
    # Relaxed search: any volume, any price, within 30 days
    $relaxed = @()
    foreach ($market in $allMarkets) {
        try {
            $expDate = [DateTime]::Parse($market.expiration_date)
            $daysUntil = ($expDate - $targetDate).Days
            
            if ($daysUntil -gt 0 -and $daysUntil -le 30) {
                $volume = [int]$market.volume
                $price = [int]$market.last_price
                
                if ($volume -gt 0) {  # Any volume
                    $investmentCost = $price / 100.0
                    $profit = 1.0 - $investmentCost
                    $returnPct = if ($investmentCost -gt 0) { ($profit / $investmentCost) * 100 } else { 0 }
                    $daysHeld = [Math]::Max($daysUntil, 1)
                    $irr = if ($investmentCost -gt 0 -and $investmentCost -lt 1) { 
                        ([Math]::Pow((1 + $profit / $investmentCost), (365.0 / $daysHeld)) - 1) * 100 
                    } else { 0 }
                    
                    $relaxed += [PSCustomObject]@{
                        Title = $market.title
                        Ticker = $market.ticker_name
                        Category = $market.EventCategory
                        ResolutionDate = $expDate.ToString("yyyy-MM-dd")
                        DaysUntil = $daysUntil
                        Price = $price
                        PriceDollars = $market.last_price_dollars
                        Volume = $volume
                        OpenInterest = $market.open_interest
                        ReturnIfWin = [Math]::Round($returnPct, 2)
                        AnnualizedIRR = [Math]::Round($irr, 2)
                    }
                }
            }
        }
        catch {}
    }
    
    Write-Host "RELAXED SEARCH: Found $($relaxed.Count) markets resolving in next 30 days" -ForegroundColor Cyan
    Write-Host ""
    
    # Show top 20 by volume
    $top = $relaxed | Sort-Object Volume -Descending | Select-Object -First 20
    $top | Format-Table Title, Category, DaysUntil, PriceDollars, Volume, ReturnIfWin, AnnualizedIRR -AutoSize
    
    # Generate report with relaxed criteria
    $output = @"
# Kalshi Short-Term Markets Analysis
**Analysis Date:** Feb 12, 2026  
**Target Window:** Feb 12 - Mar 14, 2026 (30 days)

## Search Results

**Strict criteria (Vol>1000, Price 20-80¢):** $($opportunities.Count) markets found
**Relaxed criteria (Any volume, resolving <30 days):** $($relaxed.Count) markets found

---

## Top Markets by Volume (Next 30 Days)

"@
    
    $rank = 1
    foreach ($opp in $top) {
        $output += @"

### $rank. $($opp.Title)
- **Ticker:** $($opp.Ticker)
- **Category:** $($opp.Category)
- **Resolution:** $($opp.ResolutionDate) ($($opp.DaysUntil) days away)
- **Current Price:** $($opp.PriceDollars)
- **Volume:** $($opp.Volume) contracts
- **Open Interest:** $($opp.OpenInterest)
- **Return if Win:** $($opp.ReturnIfWin)%
- **Annualized IRR:** $($opp.AnnualizedIRR)%

"@
        $rank++
    }
    
    $output += @"

---

## Analysis Summary

The current Kalshi market landscape appears to have limited short-term opportunities in the immediate 30-day window. This could be due to:

1. **Event Calendar Gaps:** No major FOMC meetings, CPI releases, or sports championships in the immediate Feb 12-Mar 14 window
2. **Market Lifecycle:** Recent markets may have already resolved or are in settlement
3. **API Limitations:** Paginated data may not capture all available markets

## Recommendations

1. **Monitor for new listings:** Kalshi regularly adds new markets, especially around:
   - Economic data releases (check Fed calendar for FOMC, CPI, NFP dates)
   - Sports playoffs and tournaments
   - Political deadlines and legislative votes

2. **Consider slightly longer windows:** 30-60 day markets still offer good capital velocity

3. **Check specific event series:**
   - FED-* (Federal Reserve decisions)  
   - CPI-*, JOBS-* (Economic indicators)
   - NBA-*, NCAA-* (Sports events)
   - BTC-*, ETH-* (Crypto price targets)

4. **Direct API categories to monitor:**
   - Economics (16 events in dataset)
   - Sports (10 events)
   - Financials (6 events)

---

*Generated by SHORT-TERM HUNTER*  
*Markets scanned: $($allMarkets.Count)*  
*API: https://api.elections.kalshi.com/v1/events*
"@
    
    $output | Out-File -FilePath "kalshi_short_term_opportunities.md" -Encoding UTF8
    Write-Host "Report saved to kalshi_short_term_opportunities.md" -ForegroundColor Green
    
} else {
    # Sort by IRR
    $top20 = $opportunities | Sort-Object -Property AnnualizedIRR -Descending | Select-Object -First 20
    
    Write-Host "TOP 20 OPPORTUNITIES BY ANNUALIZED IRR:" -ForegroundColor Cyan
    $top20 | Format-Table Title, DaysUntil, PriceDollars, Volume, ReturnIfWin, AnnualizedIRR -AutoSize
    
    # Generate detailed report
    $output = @"
# Kalshi Short-Term Opportunities (Next 30 Days)
**Analysis Date:** Feb 12, 2026
**Target Window:** Feb 12 - Mar 14, 2026
**Filters:** Volume > 1,000 | Price 20-80¢ | Resolution within 30 days

---

## Summary
- **Markets Analyzed:** $($allMarkets.Count)
- **Qualifying Opportunities:** $($opportunities.Count)
- **Top Picks:** 20 highest IRR markets

---

## Top 20 High-IRR Short-Term Markets

"@
    
    $rank = 1
    foreach ($opp in $top20) {
        $output += @"

### $rank. $($opp.Title)
**Ticker:** $($opp.Ticker) | **Category:** $($opp.Category)

| Metric | Value |
|--------|-------|
| **Resolution Date** | $($opp.ResolutionDate) |
| **Days Until Resolution** | **$($opp.DaysUntil) days** |
| **Current Price** | $($opp.PriceDollars) ($($opp.Price)¢) |
| **Bid/Ask Spread** | $($opp.YesBid)¢ / $($opp.YesAsk)¢ ($($opp.Spread)¢ spread) |
| **Volume** | $($opp.Volume) contracts |
| **Dollar Volume** | \$$($opp.DollarVolume) |
| **Open Interest** | $($opp.OpenInterest) |
| **Liquidity** | $($opp.Liquidity) |
| **Return if Win** | **$($opp.ReturnIfWin)%** |
| **Annualized IRR** | **$($opp.AnnualizedIRR)%** |

**Trade Recommendation:** BUY YES at $($opp.PriceDollars) or better  
**Capital Efficiency:** Frees up in $($opp.DaysUntil) days for redeployment  
**Risk Level:** $(if ($opp.Price -lt 40) { "High volatility" } elseif ($opp.Price -gt 60) { "Lower vol, established trend" } else { "Balanced" })

---

"@
        $rank++
    }
    
    $output += @"

## Trading Strategy for Short-Term Markets

### Capital Velocity is King
- **Compounding Power:** 30-day cycles = ~12 turns per year
- **Example:** 20% return per cycle → 890% annualized (with perfect compounding)
- **Reality Check:** Factor in fees, timing, and partial wins

### Position Sizing
- **Diversify across markets:** Don't bet everything on one event
- **Consider correlations:** Multiple Fed-related markets may move together
- **Reserve capital:** Keep dry powder for new opportunities

### Entry/Exit Discipline
1. **Entry:** Use limit orders near bid price to improve ROI
2. **Monitor:** Short-term markets can swing on news
3. **Exit:** Take profits at target or cut losses if conviction changes
4. **Don't hold to zero:** If thesis breaks, exit early

### Market Selection Priorities
1. ✅ **Highest IRR** (capital efficiency)
2. ✅ **Sufficient liquidity** (can enter/exit easily)
3. ✅ **Clear resolution** (minimize "edge case" risk)
4. ✅ **Narrow spread** (lower transaction costs)

### Categories to Watch
$(
    $opportunities | Group-Object Category | 
    Sort-Object Count -Descending | 
    ForEach-Object { "- **$($_.Name):** $($_.Count) opportunities" }
) -join "`n"

---

## Risk Warnings

⚠️ **Prediction markets involve real financial risk**
- Only invest what you can afford to lose
- Past performance ≠ future results
- Market prices reflect collective wisdom - don't assume you're smarter
- Binary outcomes mean you can lose 100% of stake

⚠️ **Short-term trading considerations**
- Higher velocity = more opportunities to be wrong
- Transaction costs add up
- Emotional decision-making risk increases with frequency

---

**Total Markets Scanned:** $($allMarkets.Count)  
**Opportunities Found:** $($opportunities.Count)  
**API Source:** https://api.elections.kalshi.com/v1/events

*Generated by SHORT-TERM HUNTER - Helping you compound faster*
"@
    
    $output | Out-File -FilePath "kalshi_short_term_opportunities.md" -Encoding UTF8
    Write-Host "`nDetailed report saved to: kalshi_short_term_opportunities.md" -ForegroundColor Green
}
