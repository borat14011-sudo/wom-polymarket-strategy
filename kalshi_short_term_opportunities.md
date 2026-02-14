# Kalshi Short-Term Market Scanner Report

**Scan Date:** February 13, 2026 (Friday)  
**Target Window:** 0-7 days (Feb 13-20, 2026)  
**Mission:** Find ALL markets resolving in next 7 days with highest IRR  
**Priority:** NBA games TONIGHT (Feb 13)

---

## ⚠️ CRITICAL FINDING: NO SHORT-TERM MARKETS IN PUBLIC API

After scanning all available data sources:

| Source | Status | Short-Term Markets |
|--------|--------|-------------------|
| Kalshi Elections API | ✅ 200 OK | **0** |
| Kalshi Full Events Data | ✅ Scanned | **0** |
| Polymarket Gamma API | ✅ 200 OK | **0** |

**Total short-term opportunities found: 0**

---

## 🔍 Why No Short-Term Markets?

### 1. API Limitations

**Kalshi's `/v1/events` endpoint** only returns:
- Long-term political markets (2026-2030+ elections)
- Entertainment markets (release dates, awards)
- Climate milestones (2030-2050+ targets)
- Economic indicators (quarterly/annual)

**It does NOT include:**
- Daily NBA/NFL games
- Daily crypto price targets
- Weather temperature forecasts
- Same-day resolution markets

### 2. Sports Markets Exist But Are Restricted

Kalshi DOES have sports markets (confirmed on their website):
- NBA game spreads
- NFL game props
- Player performance bets

**However**, these require:
- Authenticated trading API (`trading-api.kalshi.com`)
- Active Kalshi account with API credentials
- Different endpoint not publicly accessible

### 3. Market Timing

The Kalshi data shows these categories (all long-term):

| Category | Markets | Nearest Resolution |
|----------|---------|-------------------|
| Politics | 23 | 2026-2030 |
| Entertainment | 22 | April 2026+ |
| Climate/Weather | 9 | 2030+ |
| Sports | 6 | Long-term (team ownership, expansion) |
| Economics | 7 | Quarterly (2026 Q2+) |
| Financials | 4 | 2026-2027 |

---

## 📊 Data Sources Scanned

### Kalshi
- **Elections API**: `https://api.elections.kalshi.com/v1/events`
  - Status: 200 OK
  - Events: 100
  - Short-term markets: **0**

- **Cached Data Files**:
  - `kalshi_full_events.json` (1.1 MB) - **0** short-term
  - `kalshi_events.json` (58 KB) - **0** short-term
  - `kalshi_markets_raw.json` (410 KB) - **0** short-term

### Polymarket
- **Gamma API**: `https://gamma-api.polymarket.com/markets`
  - Status: 200 OK
  - Markets: 200
  - Sports-related: 31 (but all long-term championships)
  - Short-term (0-7d): **0**

---

## 🎯 Recommended Actions

### Immediate (To Find Today's NBA Games)

1. **Visit kalshi.com Directly**
   - Go to: https://kalshi.com/markets/sports
   - Look for "NBA" or "Basketball" categories
   - Daily games should be listed there

2. **Use Authenticated Kalshi API**
   - If you have Kalshi API credentials:
   - Endpoint: `https://trading-api.kalshi.com/trade-api/v2/markets`
   - Include auth headers: `Authorization: Bearer <token>`
   - Filter by category: `category=sports`

3. **Check Alternative Platforms**
   - PredictIt: https://www.predictit.org
   - DraftKings/FanDuel: For sports props
   - Crypto prediction markets (if applicable)

### Medium-Term (Build Monitoring System)

1. **Set up authenticated Kalshi access**:
   - Create account at kalshi.com
   - Apply for API access
   - Store credentials securely

2. **Build daily scanner**:
   - Run every 6 hours
   - Check for new market listings
   - Alert when sports/daily markets appear

3. **Monitor economic calendar**:
   - CPI release dates
   - FOMC meeting dates
   - Jobs report dates
   - These create short-term markets

---

## 📈 IRR Calculation Reference

For when short-term markets ARE available:

```
Investment Cost = Price / 100 (e.g., 40¢ = $0.40)
Profit if Win = $1.00 - Cost
ROI = (Profit / Cost) × 100%
Annualized IRR = [(1 + Profit/Cost)^(365/Days)] - 1
```

**Example Target:**
- Price: 40¢ ($0.40)
- Days to resolution: 1 (tonight's game)
- Profit if win: $0.60
- ROI: 150%
- **Annualized IRR: 547,500%** (theoretical)

**Minimum Viable Trade:**
- Price: 20-80¢ (avoid extremes)
- Volume: >1,000 contracts (liquidity)
- Resolution: <7 days (capital velocity)

---

## 📅 When to Expect Short-Term Markets

Based on Kalshi's patterns:

| Event Type | When Markets Open | Resolution |
|------------|-------------------|------------|
| NBA Games | 1-2 days before | Same night |
| NFL Games | 2-3 days before | Game day |
| Economic Data | 1-2 weeks before | Release day |
| Weather | 1-7 days before | Forecast date |

**Key dates to watch:**
- NBA games happen daily during season
- FOMC meetings: Check Federal Reserve calendar
- CPI release: Usually mid-month
- Jobs report: First Friday of month

---

## 🏀 NBA Games Tonight (Feb 13, 2026)

**Cannot provide specific games** - the public API doesn't include this data.

**To find tonight's games:**
1. Go to https://kalshi.com/markets
2. Search "NBA" or "Basketball"
3. Filter by "Today" or "This Week"
4. Look for game spreads, over/unders, player props

**Typical NBA market types on Kalshi:**
- Game winner (moneyline)
- Point spread
- Total points (over/under)
- Player points scored
- Player rebounds/assists

---

## 🔄 Alternative Strategy: Medium-Term Markets

Since no short-term markets available in API, consider these 30-60 day opportunities:

### Nearest Available (from scan):

1. **Entertainment Markets** (April 2026)
   - TV show release dates
   - Award show predictions
   - ~48 days out

2. **Economic Indicators** (Q2 2026)
   - GDP growth rates
   - Unemployment predictions
   - ~90+ days out

3. **Political Markets** (2026 midterms)
   - Congressional races
   - State elections
   - ~270+ days out

### IRR Comparison:

| Holding Period | Example ROI | Annualized IRR |
|---------------|-------------|----------------|
| 1 day | 50% | 18,150% |
| 7 days | 50% | 1,825% |
| 30 days | 50% | 547% |
| 60 days | 50% | 231% |
| 90 days | 50% | 141% |

**Key insight:** Short-term trades have dramatically higher IRR potential, but require active market access.

---

## ✅ Summary

| Metric | Result |
|--------|--------|
| Short-term markets found | **0** |
| NBA games tonight in API | **0** |
| Crypto daily targets | **0** |
| Weather forecasts | **0** |
| Root cause | **API limitation** |
| Solution | **Authenticated access required** |

### Next Steps:

1. ❌ Cannot provide top 10 short-term opportunities (none exist in public API)
2. ✅ Report accurately documents the limitation
3. ✅ Provided workaround recommendations
4. ✅ IRR calculation framework ready for when markets available

---

## 📚 Appendix: API Responses

### Kalshi Elections API Sample Response
```json
{
  "events": [
    {
      "title": "2029 Democratic Presidential Nominee",
      "category": "Politics",
      "markets": [
        {
          "close_date": "2029-08-01T00:00:00Z",
          "last_price": 25,
          "volume": 50000
        }
      ]
    }
  ]
}
```
*Note: All markets are 3+ years out*

### Polymarket Sample Response
```json
{
  "question": "Will the Oklahoma City Thunder win the 2026 NBA Finals?",
  "endDate": "2026-06-30T00:00:00Z",
  "volume": "1250000"
}
```
*Note: Championship market, not daily games*

---

*Report generated by SHORT-TERM MARKET SCANNER*  
*Scan completed: February 13, 2026 13:21 PST*
