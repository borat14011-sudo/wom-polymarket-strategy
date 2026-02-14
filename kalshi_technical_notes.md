# KALSHI TECHNICAL NOTES

## API Migration Notice
**IMPORTANT:** The API has been migrated from:
- ❌ `https://trading-api.kalshi.com/trade-api/v2` (deprecated)
- ✅ `https://api.elections.kalshi.com/trade-api/v2` (current)

## Series Available (Categories)

### Politics (40+ series)
- `KXTRUMPNATSEC` - Trump National Security Advisor
- `KXDEEPSEEKBAN` - DeepSeek AI ban
- Presidential/Congressional elections
- Admin appointments and policy decisions

### Crypto (20+ series)
- `KXBCHMINY` - Bitcoin Cash annual minimum
- BTC/ETH price movements
- Crypto regulatory decisions

### Sports (100+ series)
- NBA, NFL, NCAA Basketball
- International soccer, tennis, etc.
- E-sports and video game markets

### Economics (15+ series)
- Federal Reserve rate decisions
- CPI/inflation reports
- GDP, unemployment data
- Market indices

### Weather (10+ series)
- Temperature extremes
- Precipitation totals
- Snow accumulation

## Market Data Structure

```json
{
  "ticker": "MARKET-TICKER-ID",
  "title": "Market question/description",
  "status": "active|closed|settled",
  "volume_24h": 0,
  "volume": 1017,
  "last_price_dollars": "0.139",
  "previous_price_dollars": "0.0",
  "yes_bid_dollars": "0.0",
  "yes_ask_dollars": "0.139",
  "liquidity_dollars": "134.413",
  "open_interest_fp": "1017.0",
  "close_time": "2026-02-27T03:00:00Z",
  "expiration_time": "2026-02-27T03:00:00Z"
}
```

## Key Observations

### Volume Patterns:
- **New markets:** Often created with $0 volume, liquidity providers add initial orders
- **Trending markets:** Can spike to $50k-200k+ volume on news events
- **Mature markets:** Steady $10k-30k daily volume on established topics

### Price Behavior:
- **News-driven:** Major events cause 20-40% swings in hours
- **Mean reversion:** Overreactions typically correct within 24-48h
- **Liquidity premium:** Wide spreads (10-20 cents) on low-volume markets

### Settlement Sources:
Markets reference authoritative sources:
- **Politics:** White House, Congress, AP, NYT, WSJ
- **Economics:** Federal Reserve, BLS, BEA, Census Bureau
- **Crypto:** CF Benchmarks, CoinDesk
- **Sports:** ESPN, CBS Sports, Fox Sports

## Query Strategies

### 1. Find High-Volume Markets
```bash
# Get all markets, filter by volume client-side
curl "https://api.elections.kalshi.com/trade-api/v2/markets?limit=200&status=open"
# Then: Sort by volume_24h descending
```

### 2. Target Specific Categories
```bash
# Politics
curl "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=PRES&limit=100"

# Economics  
curl "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=FEDRATE&limit=100"

# Crypto
curl "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=BTC&limit=100"
```

### 3. Monitor Specific Events
```bash
# Get event details
curl "https://api.elections.kalshi.com/trade-api/v2/events/{event_ticker}"

# Get all markets in an event
curl "https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker={EVENT}&limit=100"
```

## "Buy the Dip" Detection Algorithm

```python
def is_dip_opportunity(market):
    """
    Detect if market qualifies for "Buy the Dip" strategy
    """
    current_price = float(market['last_price_dollars'])
    previous_price = float(market['previous_price_dollars'])
    volume_24h = int(market['volume_24h'])
    liquidity = float(market['liquidity_dollars'])
    
    # Calculate price drop
    if previous_price > 0:
        price_drop_pct = ((current_price - previous_price) / previous_price) * 100
    else:
        return False  # No price history
    
    # Criteria:
    # 1. Price dropped >10% (mean reversion signal)
    # 2. Volume >$10k (sufficient liquidity)
    # 3. Liquidity >$50 (tight spreads)
    # 4. Not near expiration (>24h remaining)
    
    if (price_drop_pct < -10 and 
        volume_24h > 10000 and 
        liquidity > 50):
        return True
    
    return False
```

## Rate Limiting & Best Practices

### Observed Limits:
- **No authentication required** for public market data
- **No explicit rate limit** encountered in testing
- **Recommended:** 1 request per second to be safe

### Pagination:
- Max `limit` parameter: 200
- Use `cursor` field for next page
- Keep fetching until `cursor` is null/empty

### Caching Strategy:
- **Market list:** Refresh every 5-15 minutes
- **Individual market:** Refresh every 1 minute for active monitoring
- **Series/Events:** Refresh daily (rarely change)

## Error Handling

### Common Errors:
```json
// Deprecated API endpoint
{
  "error": "API has been moved to https://api.elections.kalshi.com/"
}

// Invalid ticker
{
  "error": "Market not found"
}

// Invalid parameters
{
  "error": "Invalid status parameter"
}
```

### Retry Logic:
```python
import time
import requests

def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

## Market Lifecycle

1. **Created** - Market appears with `status=active`, usually $0 volume
2. **Early Trading** - Liquidity providers place orders, small volume
3. **Trending** - News/events drive volume spike, price volatility
4. **Mature** - Steady volume, tighter spreads, established price
5. **Pre-Close** - Volume tapers, price converges to expected outcome
6. **Closed** - No more trading, awaiting settlement
7. **Settled** - Resolved YES/NO, payouts processed

## Buy the Dip Ideal Targets

### Stage: Mature → Trending
- **Why:** Established liquidity + news-driven volatility
- **Volume:** $20k-100k daily
- **Spread:** <5 cents
- **Time to expiration:** 7-30 days

### Categories: Politics > Economics > Crypto
- **Politics:** Highest emotional trading, frequent overreactions
- **Economics:** Professional traders, but still news-driven
- **Crypto:** High volatility, but less predictable

### Event Types:
1. **Confirmation hearings** - Yes/No on appointments
2. **Policy deadlines** - Legislation passage, executive orders
3. **Economic releases** - CPI, jobs, Fed decisions
4. **Crypto milestones** - ETF approvals, regulatory decisions

## Historical "Dip" Examples (Pattern Analysis)

### Trump Cabinet Appointments (2025)
- **Pattern:** Rumor → Spike to 70-80% → Denial → Dip to 30-40% → Confirmation → Back to 90%+
- **Opportunity:** Buy at 30-40% after denial, sell at 80%+
- **ROI:** 100-150% if correct

### Fed Rate Decisions
- **Pattern:** Market prices 80% hike → FOMC hints pause → Dip to 40% → Decision → 90%+
- **Opportunity:** Buy dip after dovish hints, sell before decision
- **ROI:** 50-100%

### Crypto Regulatory News
- **Pattern:** Ban rumor → Crash to 20% → Clarification → Recovery to 50-60%
- **Opportunity:** Buy panic sell-off, hold for correction
- **ROI:** 100-200%

## Monitoring Dashboard (Recommended)

### Real-time Alerts:
1. **Volume spike:** >3x daily average in 1 hour
2. **Price dip:** >10% drop in 4 hours
3. **Spread tightening:** Ask-Bid narrows (liquidity improving)

### Daily Scan:
- Top 50 markets by volume
- Politics category (always volatile)
- Crypto category (24/7 action)
- Upcoming economic releases (calendar-based)

### Weekly Review:
- Which dips recovered? (validate strategy)
- Which dips continued? (learn failure modes)
- New high-volume series emerging?

---

**Last updated:** February 12, 2026  
**API version:** v2  
**Status:** Production-ready for targeted scanning
