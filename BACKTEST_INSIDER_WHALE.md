# INSIDER/WHALE COPY TRADING STRATEGY - BACKTEST ANALYSIS

**Date:** 2026-02-07  
**Strategy:** Copy Polysights alerts + Top traders (>70% win rate)  
**Target Period:** 2-year historical backtest (2024-02-07 to 2026-02-07)  
**Status:** ⚠️ DATA UNAVAILABLE - Forward Testing Required

---

## EXECUTIVE SUMMARY

**Result:** Historical backtest **CANNOT BE COMPLETED** with publicly available data.

**Reason:**
- Polysights historical alerts require Twitter/X API access (paid, authentication required)
- Polymarket historical trader positions not accessible via public APIs
- Blockchain data (Goldsky) requires specialized indexing infrastructure
- Historical "whale" trade entries/exits not timestamped in public leaderboards

**Claimed Performance (Unverified):**
- **Polysights:** 85% win rate (self-reported)
- **Axios Coverage:** 96% accuracy claim (needs verification)
- **Top Traders:** Current monthly P&L shown, but no historical win rate tracking

**Recommendation:** Proceed with **forward testing** using real-time data collection.

---

## DATA AVAILABILITY ASSESSMENT

### 1. Polysights Historical Alerts ❌

**Attempted:**
- Direct Twitter/X web scraping: Blocked (requires login, rate limits)
- Twitter API v2: Requires authentication + paid tier for historical search
- Archive.org snapshots: No structured data available

**What's Needed:**
- Twitter API v2 Academic/Enterprise access ($)
- Historical tweet archive from @polysights (Feb 2024 - Feb 2026)
- Parse trade alerts: market, direction, timestamp, resolution

**Barrier:** $100-500/month for Twitter API Historical Search

---

### 2. Polymarket Top Trader Historical Positions ❌

**Attempted:**
- `data-api.polymarket.com/leaderboard` - Only current snapshot
- `clob.polymarket.com/trades` - Requires specific user address + authentication
- Individual trader profiles - Only show current positions, not historical

**Current Leaderboard (Feb 2026):**
| Rank | Trader | Monthly P&L | Volume |
|------|--------|------------|--------|
| 1 | 0x4924...3782 | +$2.64M | $14.2M |
| 2 | FeatherLeather | +$1.82M | $3.4M |
| 3 | weflyhigh | +$1.07M | $6.3M |

**What's Visible:** Current month P&L, NOT historical win rates or entry/exit timestamps

**What's Needed:**
- Polymarket Data API premium access (not publicly documented)
- Or Goldsky blockchain indexing (requires infrastructure setup)
- Historical position tracking: entry price, exit price, timestamp, outcome

**Barrier:** API not available; requires blockchain indexing infrastructure

---

### 3. Goldsky Blockchain Data ⚠️

**Attempted:**
- Reviewed Goldsky documentation
- Explored Mirror, Subgraphs, Turbo pipeline options

**Finding:** 
- Goldsky provides blockchain data indexing infrastructure
- Polymarket uses Polygon blockchain for settlements
- Requires: Account setup, pipeline configuration, SQL queries
- **Not a ready-to-use historical dataset**

**What's Needed:**
- Goldsky account + pipeline setup (time: 4-8 hours)
- Index Polymarket contracts on Polygon
- Build queries to extract trader positions over 2-year period
- Join with market resolution data

**Barrier:** Time (4-8 hrs setup) + technical complexity

---

## STRATEGY DEFINITION (For Future Testing)

### Entry Signals

**Option A: Polysights Copy**
- Monitor @polysights Twitter/X for trade alerts
- Identify: Market, Direction (Yes/No), Implied edge
- Enter position within 15 minutes of alert
- Position size: $1,000 per alert (normalized)

**Option B: Top Trader Copy**
- Identify traders with 70%+ monthly win rate
- Track new positions via blockchain/API
- Copy positions with >$10,000 size (whale threshold)
- Position size: Match 10% of whale's position

### Exit Rules

1. **+20% Profit Target:** Lock in gains
2. **Whale Exit:** Exit when copied trader sells >50% of position
3. **Market Resolution:** Auto-exit on resolution
4. **Max Hold:** 30 days (prevent capital lock)

---

## THEORETICAL BACKTEST SIMULATION

Since real data is unavailable, here's what the backtest **would** calculate:

### Metrics to Track

1. **Win Rate:** % of trades that profit
2. **Average Win:** Mean profit on winning trades
3. **Average Loss:** Mean loss on losing trades
4. **Sharpe Ratio:** Risk-adjusted returns
5. **Max Drawdown:** Worst peak-to-trough decline
6. **Total Return:** Net P&L over 2 years
7. **Trade Frequency:** Avg trades per week

### Expected Profile (Based on Claims)

**Polysights (85% win rate claim):**
- ~400 alerts over 2 years (4/week)
- 340 wins, 60 losses
- Avg win: +15% (est.)
- Avg loss: -8% (est.)
- **Theoretical Return:** +180% over 2 years

**Top Traders (observed P&L):**
- Top 10 avg monthly P&L: +$800K
- If 70% win rate sustained over 24 months
- **Est. Annual Return:** 40-60% on $1M bankroll

---

## WHY THIS MATTERS

### Survivorship Bias Warning ⚠️

Current leaderboard shows **winners**. Historical backtest would reveal:
- Traders who blew up mid-2024
- Polysights alerts that failed
- True risk-adjusted performance

**Without historical data:**
- Only see current top performers
- Miss traders who had -80% months
- Cannot validate 85% / 96% accuracy claims

---

## ALTERNATIVE: FORWARD TESTING PLAN

### Phase 1: Data Collection (30 days)

**Polysights Monitoring:**
- Set up Twitter/X alerts for @polysights
- Log every alert: timestamp, market, direction, reasoning
- Track resolution outcomes
- Calculate real-time win rate

**Top Trader Tracking:**
- Monitor top 20 leaderboard traders daily
- Track position changes via Polymarket UI
- Log: entry, exit, P&L per trade
- Calculate individual trader win rates

**Tools Needed:**
- Twitter API or manual logging spreadsheet
- Daily leaderboard snapshots (automated script)
- Blockchain transaction monitoring (optional)

### Phase 2: Paper Trading (Days 31-60)

- Simulate trades with $100K virtual bankroll
- Follow strategy rules strictly
- Track all metrics in real-time
- Compare to claimed performance

### Phase 3: Live Testing (Days 61-90)

- Start with $1K-5K real capital
- Scale if performance matches theoretical
- Implement risk management (stop-losses, position limits)

---

## CRITICAL QUESTIONS FOR STRATEGY VIABILITY

### 1. Timing Edge: Can You Execute Fast Enough?

**Challenge:** Polysights has 200K+ followers
- When alert drops, odds may shift within minutes
- Front-running by bots/APIs
- **Question:** What's the alpha decay time?

**Test:** Track odds movement after alerts
- If odds move >5% in 5 minutes → edge likely eroded
- If stable for 30+ minutes → copyable

### 2. Position Size: Can You Match Whale Scale?

**Challenge:** Top traders move millions
- $5M position = significant market impact
- Small copier with $10K may not get same fills
- **Question:** Does strategy work at $10K-100K scale?

**Test:** Check order book depth
- For markets with <$50K liquidity → harder to copy whales
- For markets with >$500K liquidity → more scalable

### 3. Selection Bias: Are Claims Cherry-Picked?

**Polysights 85% claim:**
- Based on what sample size?
- Over what time period?
- Including all alerts or just "high confidence"?

**Axios 96% claim:**
- Likely cherry-picked specific markets (e.g., politics)
- May exclude sports, crypto (more volatile)

**Verification Needed:** Independent audit of alerts

---

## RISK FACTORS

### 1. Information Asymmetry
- Insiders may have edge you lack
- By the time alert is public, edge may be gone

### 2. Market Manipulation
- Whale could pump/dump to trap copiers
- "Smart money" isn't always right

### 3. Liquidity Risk
- Cannot exit when whale exits (slippage)
- Especially on smaller markets

### 4. Platform Risk
- Polymarket rule changes
- Market resolution disputes

### 5. Regulatory Risk
- Prediction markets legal gray area
- Potential shutdown (see PolyMarket FBI raid 2024)

---

## TECHNICAL IMPLEMENTATION NOTES

If historical data becomes available, backtest code should include:

```python
# Pseudocode for backtest engine

def backtest_insider_strategy(alerts, trader_positions, market_data):
    portfolio = Portfolio(initial_capital=100000)
    
    for alert in alerts:
        # Entry
        market = get_market(alert.market_id)
        entry_price = market.get_price_at(alert.timestamp)
        position = portfolio.open_position(
            market=market,
            direction=alert.direction,
            size=1000,  # Fixed size
            entry_price=entry_price
        )
        
        # Exit logic
        for day in range(alert.timestamp, market.resolution_date):
            current_price = market.get_price_at(day)
            pnl_pct = (current_price - entry_price) / entry_price
            
            # Exit conditions
            if pnl_pct >= 0.20:  # +20% target
                portfolio.close_position(position, reason="profit_target")
                break
            
            if whale_exited(alert.whale_id, market, day):
                portfolio.close_position(position, reason="whale_exit")
                break
        
        # Force close on resolution
        if position.open:
            portfolio.close_position(position, reason="resolution")
    
    return portfolio.calculate_metrics()
```

---

## CONCLUSION

### Current Status: DATA UNAVAILABLE

**Cannot complete 2-year historical backtest without:**
1. Polysights Twitter archive (cost: $100-500/mo for API)
2. Polymarket historical positions (requires blockchain indexing)
3. Significant time investment (8-16 hours setup)

### Claimed Performance (Unverified)

- **Polysights:** 85% win rate
- **Axios:** 96% accuracy
- **Top Traders:** Consistent monthly gains visible

**⚠️ Without independent verification, treat claims with skepticism**

### Recommended Next Steps

1. **Forward Test (30-90 days):** Track real-time data
2. **Small Capital Test:** $1K-5K to validate
3. **Compare to Baseline:** Buy-and-hold top markets vs. copy strategy
4. **Measure Alpha Decay:** How fast do edges disappear post-alert?

### Final Assessment

**Strategy Viability:** ⚠️ UNPROVEN
- **High theoretical win rates** (if claims accurate)
- **Execution risk** (timing, liquidity, slippage)
- **Data transparency** (poor historical tracking)

**Recommendation:** 
- **DO NOT deploy significant capital** based on unverified claims
- **START with forward testing** to collect real data
- **Allocate <5% of trading capital** for initial testing
- **Require 3+ months of real data** before scaling

---

## APPENDIX: Data Sources Attempted

### Successfully Accessed
- ✓ Polymarket current leaderboard (snapshot)
- ✓ Current top 20 traders + monthly P&L
- ✓ Individual trader profiles (current positions only)
- ✓ API documentation (endpoints, structure)

### Failed to Access
- ✗ Polysights historical tweet archive
- ✗ Historical trader positions (entry/exit data)
- ✗ Historical market odds over time
- ✗ Blockchain transaction history (whale tracking)

### Tools Required for Completion
1. **Twitter API v2** (Academic/Enterprise tier) - $100-500/mo
2. **Goldsky Pipeline** - Setup time 4-8 hours
3. **Polymarket Premium API** (if exists) - Unknown cost
4. **Manual Data Collection** - 40+ hours for 2-year period

---

**Report Generated:** 2026-02-07  
**Analyst:** OpenClaw Subagent (backtest-insider)  
**Time Invested:** 20 minutes (investigation phase)  
**Status:** Incomplete - awaiting data access or forward testing approval
