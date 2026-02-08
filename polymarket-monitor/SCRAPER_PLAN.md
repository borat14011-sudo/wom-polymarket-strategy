# Historical Data Scraper - Execution Plan

**Date:** Feb 7, 2026, 8:30 AM PST  
**Repo:** benjiminii/polymarket-scrape (updated Feb 6, 2026)  
**Location:** `polymarket-monitor/historical-data-scraper/`

---

## Setup Status

✅ Git clone complete  
⏳ Dependencies installing (pandas, aiohttp, duckdb, streamlit, polars, pyarrow, rich)  
⏳ Waiting for pip to finish (~1-2 min remaining)

---

## Execution Plan

### Step 1: Run Full Scrape
```bash
cd polymarket-monitor/historical-data-scraper
python run.py all
```

**What it does:**
- Fetches ALL events from Gamma API (active + resolved)
- Downloads price history for every token via CLOB API
- Transforms to Parquet format
- Stores in `data/` folder

**Expected output:**
- `data/events_raw.json` (all events metadata)
- `data/prices_raw.json` (all price histories)
- `data/polymarket_complete.json` (combined dataset)
- `data/events.parquet` (optimized events)
- `data/prices.parquet` (optimized prices)

**Time:** 10-30 minutes (depends on total markets)  
**Size:** 500MB - 2GB

---

## Step 2: Validate Data

Run quick DuckDB queries to verify:

```python
import duckdb

# Check events
duckdb.sql("""
    SELECT 
        COUNT(*) as total_events,
        COUNT(DISTINCT event_id) as unique_events,
        MIN(start_date) as earliest,
        MAX(end_date) as latest,
        SUM(closed::int) as resolved_count
    FROM 'data/events.parquet'
""").show()

# Check prices
duckdb.sql("""
    SELECT 
        COUNT(*) as total_prices,
        COUNT(DISTINCT market_id) as unique_markets,
        MIN(timestamp) as earliest_price,
        MAX(timestamp) as latest_price
    FROM 'data/prices.parquet'
""").show()

# Find Iran market
duckdb.sql("""
    SELECT title, slug, volume, end_date, closed
    FROM 'data/events.parquet'
    WHERE LOWER(title) LIKE '%iran%' AND LOWER(title) LIKE '%strike%'
""").show()
```

---

## Step 3: Re-run Backtests with REAL Data

Once data is validated, deploy 7 agents to re-backtest ALL strategies on real historical data:

1. **Trend Filter** (Grade A candidate)
2. **Time Horizon** (Grade A candidate)  
3. **NO-Side Bias** (Grade C - small sample)
4. **Expert Fade** (Grade C - small sample)
5. **News Reversion** (Grade D - simulated timestamps)
6. **Pairs Trading** (Grade D - synthetic CoinGecko data)
7. **Insider/Whale** (pending Agent #9)

**Expected Changes:**
- Win rates will DROP (real data is harder than synthetic)
- Some strategies will FAIL completely
- Drawdowns will be LARGER
- Only 2-3 strategies likely to remain Grade A

**Realistic Expectations:**
- 55-65% win rates (not 70-80%)
- -25 to -35% max drawdown (not -10%)
- Sharpe ratios 1.5-2.5 (not 3+)

---

## Step 4: Update Documentation

After real backtests complete:
- Update `FINAL_STRATEGY_REPORT.md`
- Update `MEMORY.md` with validated findings
- Create `REAL_VS_SYNTHETIC_COMPARISON.md`
- Telegram alert with summary

---

## Step 5: Deploy Live Monitoring

With validated strategies:
- Activate 5-minute cron monitoring
- Deploy Grade A filters immediately
- Paper test Grade C strategies for 30 days
- Hold Grade D strategies until validated

---

## Data Schema (Expected)

### events.parquet
- ~2,000-5,000 events (Oct 2023 - Feb 2026)
- Columns: event_id, slug, title, description, volume, closed, start_date, end_date, liquidity

### prices.parquet
- ~100,000-500,000 price observations
- Columns: market_id, token_id, timestamp, price, token_type
- Fidelity: 60 minutes (hourly candles)

---

## Success Criteria

✅ Data spans 2+ years (back to Oct 2023 or earlier)  
✅ Iran market found in resolved markets  
✅ >1,000 events with price data  
✅ >100,000 price observations  
✅ All DuckDB queries execute in <1 second  
✅ Real backtests complete in <30 minutes (parallel agents)  
✅ At least 2 strategies achieve Grade A on real data

---

**Status:** Waiting for pip install to complete...  
**Next:** Run `python run.py all` immediately after install finishes
