# 📊 HISTORICAL DATA INVENTORY - Complete Archaeological Report
**Generated:** 2026-02-12 17:28 PST  
**Mission:** Comprehensive inventory of all backtestable historical Polymarket data

---

## 🎯 EXECUTIVE SUMMARY

### Total Data Available
- **191,483 events** with market data (polymarket_complete.json)
- **93,949 markets** in snapshot (78,654 closed, 15,295 active)
- **17,324 markets** with historical price data (backtest_dataset_v1.json)
- **500 resolved markets** with detailed outcomes (RESOLVED_DATA_FIXED.json)
- **172 resolved markets** in CSV format
- **2,015+ backtest trades** already executed across multiple CSVs
- **$35.17 BILLION** total market volume captured

---

## 📁 PRIMARY DATA SOURCES

### 1. **polymarket_complete.json** ⭐⭐⭐⭐⭐
**Path:** `polymarket-monitor/historical-data-scraper/data/polymarket_complete.json`  
**Size:** 511.4 MB  
**Records:** 191,483 events  

**Content:**
- Complete event and market data from Polymarket
- Each event contains multiple markets
- Includes: event_id, slug, title, description, start_date, end_date, closed status, volume
- Markets nested within events with questions, outcomes, prices, token_ids
- Price history data structure (though many appear empty in sample)

**Backtesting Value:** ⭐⭐⭐⭐⭐  
**Date Range:** 2024-2026 (estimated from samples)  
**Gap:** Price histories appear incomplete in structure - needs validation

---

### 2. **backtest_dataset_v1.json** ⭐⭐⭐⭐⭐
**Path:** `polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json`  
**Size:** 189.8 MB (single line JSON)  
**Records:** 17,324 markets  

**Content:**
```json
{
  "event_id": "200970",
  "market_id": "1349943",
  "question": "Will Elon Musk post 0-19 tweets...",
  "volume": 340146.815595,
  "start_date": "2026-02-07T05:11:27.402581Z",
  "end_date": "2026-02-17T17:00:00Z",
  "closed": false,
  "outcome": null,
  "price_history": [
    {"t": 1770442251, "p": 0.0015},
    {"t": 1770442836, "p": 0.0015},
    ...
  ],
  "token_id": "..."
}
```

**Data Fields:**
- ✅ event_id, market_id, question
- ✅ volume (in USD)
- ✅ start_date, end_date
- ✅ closed status
- ✅ outcome (Yes/No or null)
- ✅ **price_history** with timestamps and prices
- ✅ token_id for API calls

**Backtesting Value:** ⭐⭐⭐⭐⭐  
**PERFECT FOR BACKTESTING** - Has timestamped price history!  
**Date Range:** 2024-02-07 to 2026-02-17  
**Estimated Datapoints:** Millions of price points across 17K+ markets

---

### 3. **markets_snapshot_20260207_221914.json** ⭐⭐⭐⭐
**Path:** `markets_snapshot_20260207_221914.json`  
**Size:** 2.44 GB (single line)  
**Records:** 93,949 total markets  

**Summary Stats:**
- Total markets: 93,949
- Active markets: 15,295
- Closed markets: 78,654
- Total volume: $35,172,430,427.50
- Collection time: 2026-02-07 22:19:13 UTC
- Target year filter: 2024
- Min volume filter: $100

**Volume Distribution:**
- < $1K: 14,233 markets
- $1K - $10K: 29,002 markets
- $10K - $100K: 32,780 markets
- $100K - $1M: 14,591 markets
- > $1M: 3,343 markets

**Sample Market Structure:**
```json
{
  "id": "253573",
  "question": "Will Solana Network go down in January?",
  "slug": "will-solana-go-down-in-january",
  "created_at": "2024-01-02T18:26:20.426Z",
  "end_date": "2024-01-31T00:00:00Z",
  "closed": true,
  "volume": 61630.36,
  "outcomes": ["Yes", "No"],
  "outcome_prices": [0.0, 1.0],
  "last_trade_price": 0.0,
  "price_change_1h/24h/7d": ...
}
```

**Backtesting Value:** ⭐⭐⭐⭐  
**Has:** Market metadata, final prices, volume  
**Missing:** Historical price series (only final/current prices)  
**Best Use:** Filtering markets by volume, identifying resolved markets

---

### 4. **Price Checkpoint Files** ⭐⭐⭐
**Path:** `polymarket-monitor/historical-data-scraper/data/prices_checkpoint_*.json`  

**Files:**
- prices_checkpoint_5000.json - 5.5 MB (5,000 records)
- prices_checkpoint_10000.json - 37.3 MB (10,000 records)
- prices_checkpoint_15000.json - 79.7 MB (15,000 records)
- prices_checkpoint_20000.json - 127.3 MB (20,000 records)
- prices_checkpoint_25000.json - 173.5 MB (25,000 records)
- prices_checkpoint_30000.json - 240.3 MB (30,000 records)
- prices_checkpoint_35000.json - 314.6 MB (35,000 records)
- prices_checkpoint_40000.json - 372.3 MB (40,000 records)
- prices_checkpoint_41000.json - 11.7 MB (41,000 records)
- prices_checkpoint_45000.json - 26.3 MB (45,000 records)

**Total:** ~1.4 GB of price checkpoint data  
**Total Records:** 45,000+ token price histories  

**Structure:**
```json
{
  "token_id": "73509254372240515476139823732607455442580306972224926233018397621601981548880",
  "prices": [],
  "success": true
}
```

**Backtesting Value:** ⭐⭐⭐  
**Issue:** Many appear to have empty price arrays in samples  
**Status:** Needs further investigation - may be partial/failed scrapes

---

### 5. **RESOLVED_DATA_FIXED.json** ⭐⭐⭐⭐
**Path:** `RESOLVED_DATA_FIXED.json`  
**Size:** 244.5 KB  
**Records:** 500 resolved markets  

**Structure:**
```json
{
  "analysis_date": "...",
  "total_markets_analyzed": 500,
  "date_range": {...},
  "favorite_performance": {...},
  "extreme_probabilities": {...},
  "market_distribution": {...},
  "category_breakdown": {...},
  "price_statistics": {...},
  "volume_statistics": {...},
  "key_insights": [...],
  "market_details": [500 markets with outcomes]
}
```

**Backtesting Value:** ⭐⭐⭐⭐  
**Has:** 500 resolved markets with final outcomes  
**Best Use:** Validating backtest results against actual resolutions

---

## 📈 BACKTEST RESULT FILES

### Completed Backtest CSVs

#### **1. backtest_analysis.csv** ⭐⭐⭐⭐⭐
**Size:** 487 KB  
**Lines:** 2,015 trades  
**Strategies:** Trend Filter, Expert Fade, News Mean Reversion, Time Horizon, NO-Side Bias, Whale Copy  

**Fields:**
- index, strategy, market_id, entry_date, exit_date
- entry_price, exit_price, outcome
- pnl, roi, holding_days
- roi_raw, roi_adj, daily_return
- cumulative, peak, drawdown

**Sample:**
```csv
367,Time Horizon,market_143,2024-10-05,2024-10-06 18:00:00,0.877,0.906,YES,0.122,0.140,1.75
```

**Backtesting Value:** ⭐⭐⭐⭐⭐  
**This is GOLD** - Actual backtest results with full P&L metrics!

---

#### **2. backtest_results.csv**
**Size:** 278 KB  
**Lines:** 2,016 trades  
**Strategies:** Trend Filter (appears to be single-strategy results)  

**Fields:** strategy, market_id, entry_date, exit_date, entry_price, exit_price, outcome, pnl, roi

---

#### **3. event_based_trades.csv**
**Size:** 59 KB  
**Lines:** 240 trades  

**Fields:**
- strategy, market_id, entry_time, exit_time
- entry_price, exit_price, position_size
- gross_pnl, slippage_cost, fee_cost, net_pnl
- roi, hold_time_hours

**Sample:**
```csv
Trend Filter,market_32,2024-10-02 12:00:00,2024-10-05 05:02:55,-451.60,-1.054,65.05
```

**Includes Transaction Costs!** Slippage and fees modeled  
**Date Range:** Oct-Nov 2024

---

#### **4. trades_by_time_bucket.csv**
**Size:** 105 KB  
**Lines:** 1,193 trades  

**Buckets:** <3d, 3-7d, 7-30d, >30d  
**Fields:** Time Bucket, Market, Entry Date, Exit Date, Days Held, Win, P&L, P&L %, Volume

**Sample:**
```csv
<3d,Michigan Senate Election Winner,2024-11-04,2024-11-05,1,Yes,9.08,9.1,394971.30
```

**Backtesting Value:** ⭐⭐⭐⭐  
**Shows time-horizon impact on returns**

---

#### **5. Strategy-Specific Trade CSVs**
- **trades_trend_filter.csv** - 69.7 KB (largest single-strategy file)
- **trades_news.csv** - 3.6 KB
- **trades_expert_fade.csv** - 2.8 KB
- **trades_insider.csv** - 2.7 KB
- **trades_pairs.csv** - 2.3 KB
- **trades_no_side.csv** - 2.1 KB

---

### Backtest Result JSONs

**Path:** `backtest-results/`

- **expert_fade_results.json** - 15.4 KB
- **news_reversion_results.json** - 16.0 KB
- **no_side_bias_results.json** - 15.4 KB
- **pairs_trading_results.json** - 13.6 KB
- **time_horizon_results.json** - 13.3 KB
- **trend_filter_results.json** - 14.1 KB
- **whale_tracking_results.json** - 16.5 KB
- **FINAL_REPORT.json** - 2.6 KB

**Total:** 7 strategy backtest results with summary statistics

---

## 🗃️ RESOLVED MARKETS DATA

### **polymarket_resolved_markets.csv**
**Size:** 80.9 KB  
**Lines:** 172 markets  

**Fields:**
```csv
event_id,event_title,event_slug,event_end_date,market_id,condition_id,question,
outcomes,final_prices,winner,closed,volume_usd,volume_num,clob_token_ids,
description,created_time
```

**Sample:**
```csv
903799,Michigan Senate Election Winner,michigan-us-senate-election-winner,
2024-11-05T12:00:00Z,255448,0x673b...,Will a Democrat win Michigan US Senate Election?,
Yes|No,1|0,Yes,True,394971.301424,...
```

**Date Range:** 2024 elections (Michigan, Trump polls, etc.)  
**Backtesting Value:** ⭐⭐⭐⭐⭐  
**Perfect ground truth for validating predictions**

---

### **oct_2025_resolved.csv**
**Size:** 31.8 KB  
**Lines:** 179 markets  

**October 2025 resolved markets** - Canadian election outcomes  
**Most volume = 0** (low-volume markets)

---

### **resolved_markets_enriched.csv**
**Size:** 80.6 KB  
Similar to polymarket_resolved_markets.csv with additional enrichment

---

## 📊 MARKET SNAPSHOT FILES

### **Raw Market Data**
- **markets_raw.json** - 2.87 GB
- **clob-markets.json** - 1.82 GB  
- **clob-sampling.json** - 2.36 GB
- **markets_2025_2026.json** - 627.9 KB
- **gamma_markets_20260208_122125.json** - 142.2 KB
- **events.json** - 60.0 KB (event metadata)

---

### **Live Market Snapshots**
- **active-markets.json** - 648.0 KB
- **live_opportunities_snapshot.json** - 191.2 KB
- **live_markets_now.json** - 18.8 KB
- **markets.json** - 53.4 KB

---

## 🐋 SPECIALIZED DATA

### **Whale Tracking**
- **ELON_MARKETS_FOUND.json** - 59.4 KB
- **FRESH_BETS_TOP10.json** - 76.8 KB
- **top_10_bets_fixed.json** - 29.3 KB

### **Event Radar Results**
- Multiple agent results in `polymarket-monitor/backtest-results/`:
  - agent1_event_radar.json - 16.8 KB
  - agent2_event_radar.json - 18.0 KB
  - event_radar_inputs.json - 82.3 KB

### **Paper Trading**
- **ACTIVE_PAPER_TRADES.json** - 1.4 KB
- **PAPER_TRADE_LOG.json** - 4.7 KB
- **PAPER_TRADE_LOG.csv** - 2.5 KB
- **paper_trader_balance.json** - 419 bytes

---

## 📉 ECONOMIC ANALYSIS DATA

**Path:** `economic_analysis/data/`

**Performance Analytics:**
- annual_summary.csv
- monthly_performance.csv - 2.0 KB
- cumulative_performance.csv
- strategy_breakdown.csv - 1.2 KB
- trade_statistics.csv

**Risk Metrics:**
- risk_metrics.csv - 633 bytes
- drawdown_events.csv - 448 bytes
- var_analysis.csv
- scenario_sensitivity.csv

**Return Analytics:**
- return_calculations.csv
- return_statistics.csv
- kelly_criterion.csv

**Cost Analysis:**
- cost_breakdown.csv
- irr_cashflows.csv - 774 bytes

---

## 🎯 DATA GAPS & LIMITATIONS

### ✅ STRONG Coverage
1. **Resolved market outcomes** - 500+ markets with confirmed results
2. **Backtest trade logs** - 2,000+ executed trades with full metrics
3. **Market metadata** - 93K+ markets with volume, dates, categories
4. **Historical price data** - 17K+ markets in backtest_dataset_v1.json

### ⚠️ WEAK/MISSING Coverage
1. **Price checkpoint files** - Many appear to have empty price arrays (needs validation)
2. **Real-time tick data** - No raw orderbook or trade-by-trade data
3. **Liquidity metrics** - Limited depth/spread data in historical records
4. **Event outcomes** - Only 172-500 resolved vs 93K total markets
5. **Date range** - Heavy bias toward 2024-2026, limited 2022-2023 data

### 🔍 NEEDS INVESTIGATION
1. **events_raw.json** - 2.74 GB file (too large to read) - could contain critical data
2. **Price history completeness** - backtest_dataset_v1.json has price_history arrays but need to verify coverage
3. **polymarket_complete.json** - price_histories structure appears malformed in samples

---

## 💎 BEST DATA FOR BACKTESTING

### Tier 1: READY TO USE ⭐⭐⭐⭐⭐
1. **backtest_dataset_v1.json** - 17,324 markets with timestamped price histories
2. **backtest_analysis.csv** - 2,015 trades with full P&L, drawdown metrics
3. **polymarket_resolved_markets.csv** - 172 markets with verified outcomes
4. **RESOLVED_DATA_FIXED.json** - 500 markets with detailed outcome analysis

### Tier 2: VALUABLE SUPPLEMENTARY ⭐⭐⭐⭐
1. **markets_snapshot_20260207_221914.json** - 93K markets for filtering/discovery
2. **event_based_trades.csv** - 240 trades with transaction cost modeling
3. **Strategy result JSONs** - 7 files with aggregated strategy performance
4. **trades_by_time_bucket.csv** - Time horizon analysis results

### Tier 3: NEEDS PROCESSING ⭐⭐⭐
1. **polymarket_complete.json** - 191K events (needs price history extraction)
2. **Price checkpoint files** - 45K tokens (needs validation of price arrays)
3. **events_raw.json** - 2.74 GB (too large, unknown structure)

---

## 📊 ESTIMATED TOTAL BACKTEST CAPACITY

### Markets Available for Backtesting
- **High confidence (with price history):** 17,324 markets
- **Medium confidence (with snapshots):** 93,949 markets
- **Potential (needs extraction):** 191,483 events

### Ground Truth Outcomes
- **Verified resolved markets:** 500-672 markets
- **Coverage ratio:** ~0.7% of total markets have verified outcomes

### Historical Trades Available
- **Completed backtest trades:** 2,015+ trades
- **Unique strategies tested:** 7+ (Trend Filter, Expert Fade, News Reversion, etc.)
- **Date range of backtests:** October 2024 - February 2026

### Total Data Volume
- **JSON data:** ~4.5 GB
- **CSV data:** ~1.5 MB
- **Total files inventoried:** 120+ relevant files

---

## 🚀 RECOMMENDED NEXT STEPS

### Immediate Actions
1. **Validate backtest_dataset_v1.json** - Spot-check 10-20 markets to verify price_history completeness
2. **Extract polymarket_complete.json** - Parse price history data if present
3. **Investigate events_raw.json** - May contain critical historical data (2.74 GB!)
4. **Merge resolved outcomes** - Cross-reference 500 resolved markets with backtest_dataset

### Data Enhancement
1. **Download missing price histories** - For high-volume markets without historical data
2. **Scrape additional resolutions** - Expand from 500 to 2,000+ verified outcomes
3. **Calculate additional features** - Volatility, momentum, liquidity metrics from price histories

### Backtesting Pipeline
1. **Load backtest_dataset_v1.json** - 17K markets with price histories
2. **Filter by resolved outcomes** - Match with RESOLVED_DATA_FIXED.json
3. **Run strategies** - Test on verified ground truth
4. **Validate against existing results** - Compare with backtest_analysis.csv

---

## 📝 FILE PRIORITY MATRIX

| File | Size | Records | Price History | Outcomes | Priority | Status |
|------|------|---------|---------------|----------|----------|--------|
| backtest_dataset_v1.json | 190 MB | 17,324 | ✅ Yes | Partial | **P0** | ✅ Ready |
| RESOLVED_DATA_FIXED.json | 245 KB | 500 | ❌ No | ✅ Yes | **P0** | ✅ Ready |
| backtest_analysis.csv | 487 KB | 2,015 | ❌ No | ✅ Yes | **P0** | ✅ Ready |
| markets_snapshot_20260207.json | 2.44 GB | 93,949 | ❌ No | Partial | **P1** | ✅ Ready |
| polymarket_complete.json | 511 MB | 191,483 | ⚠️ Maybe | Partial | **P1** | ⚠️ Verify |
| events_raw.json | 2.74 GB | ??? | ??? | ??? | **P1** | ❌ Unknown |
| price_checkpoint_*.json | 1.4 GB | 45,000 | ⚠️ Maybe | ❌ No | **P2** | ⚠️ Verify |
| polymarket_resolved_markets.csv | 81 KB | 172 | ❌ No | ✅ Yes | **P2** | ✅ Ready |

---

## 🎯 FINAL ASSESSMENT

### Data Richness: ⭐⭐⭐⭐ (4/5)
**You have excellent data for backtesting!**

**Strengths:**
- 17K+ markets with timestamped price histories
- 500+ verified market outcomes for ground truth
- 2K+ completed backtest trades for validation
- 93K+ market metadata for filtering and discovery
- Multiple strategy results for comparison

**Weaknesses:**
- Only ~0.7% of markets have verified outcomes
- Price checkpoint files may be incomplete
- Missing detailed orderbook/liquidity data
- Date range heavily weighted to 2024-2026

### Recommendation: ✅ PROCEED WITH BACKTESTING
**You have sufficient historical data to:**
1. Backtest 7+ strategies on 17K+ markets
2. Validate against 500+ known outcomes
3. Compare results with 2K+ existing trades
4. Analyze $35B+ in trading volume

**Critical Path:**
1. Load backtest_dataset_v1.json (17,324 markets)
2. Match with RESOLVED_DATA_FIXED.json (500 outcomes)
3. Run backtests
4. Validate against backtest_analysis.csv

---

**Report Complete. Ready to mine for alpha! 🚀**
