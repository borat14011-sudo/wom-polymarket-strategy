# Polymarket Bot Detection & Mirroring Strategy

**Author:** Research Subagent  
**Date:** 2026-02-07  
**Version:** 1.0

## Executive Summary

This document outlines a comprehensive strategy for detecting algorithmic traders on Polymarket and implementing a mirroring system to capitalize on profitable bot activity. The strategy leverages Polymarket's CLOB (Central Limit Order Book) WebSocket feeds, historical trade data, and advanced pattern recognition to identify and track high-performing algorithmic traders.

**Expected Edge:** 2-5% annual returns above baseline (conservative estimate) from early signal detection and reduced adverse selection. Top-decile bots may provide 10-15%+ edge during high-activity periods.

---

## 1. Bot Detection Techniques

### 1.1 Timing-Based Signals

#### Microsecond Precision
- **Pattern:** Bots exhibit highly consistent order submission timing (within milliseconds)
- **Detection Method:** Calculate inter-arrival times between orders from same address
  - Standard deviation < 50ms suggests algorithmic execution
  - Human traders: StdDev typically > 500ms
- **Implementation:**
  ```python
  # Pseudocode
  def detect_timing_precision(order_stream):
      arrivals = [order.timestamp for order in order_stream]
      inter_arrivals = np.diff(arrivals)
      return np.std(inter_arrivals) < THRESHOLD_MS
  ```

#### Time-of-Day Patterns
- **Pattern:** Bots operate 24/7 or in highly regular schedules
- **Detection Metrics:**
  - Orders placed outside human trading hours (2-8 AM EST)
  - No "lunch break" or weekend gaps typical of humans
  - Consistent hourly distribution (Chi-squared test for uniformity)
- **Red Flag:** >90% uptime or perfect 24-hour distribution

#### Response Latency to Market Events
- **Pattern:** Sub-second response to orderbook changes, news, or price movements
- **Detection:**
  - Monitor WebSocket `last_trade_price` and `price_change` events
  - Measure time delta between market event and trader response
  - Bots: typically <100ms
  - Humans: typically >1000ms
- **Data Source:** Polymarket WebSocket `market` channel

### 1.2 Order Size & Price Patterns

#### Fixed Size Orders
- **Pattern:** Bots use programmatic position sizing
- **Detection Signals:**
  - Repeated orders of identical size (e.g., always $100 or 50 shares)
  - Size follows mathematical patterns (powers of 2, Fibonacci)
  - Little variation in order size distribution
- **Metric:** Coefficient of variation in order sizes < 0.15

#### Price Clustering
- **Pattern:** Limit orders at mathematically precise levels
- **Detection:**
  - Orders consistently at round numbers (0.50, 0.75) or tick increments
  - Price optimization algorithms (e.g., always 1 tick above best bid)
  - Lack of "fat finger" errors or psychological pricing
- **Implementation:** Analyze order price distribution, look for spikes at specific levels

#### Inventory Management Signals
- **Pattern:** Systematic position flattening and delta-neutral behavior
- **Detection:**
  - Monitor net position changes via Polymarket subgraph
  - Identify addresses that rarely hold overnight positions
  - Detect pairs trading (simultaneous YES/NO positions across correlated markets)
- **Data Source:** Polymarket Subgraph (GraphQL) for position history

### 1.3 Orderbook Interaction Patterns

#### Quote Stuffing / Layering
- **Pattern:** Rapid order placement and cancellation to probe liquidity
- **Detection Metrics:**
  - Order-to-trade ratio > 10:1
  - Cancellation rate > 80%
  - Orders canceled within <1 second of placement
- **Data Source:** WebSocket `price_change` events (track hash changes)

#### Maker vs Taker Behavior
- **Pattern:** Sophisticated bots prefer maker orders for rebates
- **Detection:**
  - Calculate maker/taker ratio from trade history
  - Bots: typically >70% maker orders
  - API: Use `get_trades()` with authenticated client, analyze `side` field

#### Spread Participation
- **Pattern:** Algorithmic market making with tight spreads
- **Detection:**
  - Consistent presence on both bid and ask
  - Spread width follows volatility patterns
  - Monitor `best_bid_ask` WebSocket messages
- **Red Flag:** Always within 1-2 ticks of mid price on both sides

### 1.4 Multi-Market Correlation

#### Simultaneous Trading
- **Pattern:** Coordinated trades across related markets
- **Detection:**
  - Identify correlated markets (e.g., "Biden wins" vs "Trump wins")
  - Detect simultaneous order placement (within 1 second)
  - Look for arbitrage between related outcomes
- **Implementation:**
  ```python
  # Track same address across multiple token_ids
  def detect_multi_market_bot(address):
      markets = get_active_markets_for_address(address)
      if len(markets) > 5 and correlation(trade_times) > 0.8:
          return True  # Likely sophisticated bot
  ```

#### News/Event Response
- **Pattern:** Immediate reaction to information events
- **Detection:**
  - Subscribe to Polymarket RTDS (Real-Time Data Socket)
  - Monitor comment activity and crypto price feeds
  - Correlate major price movements with trader responses
  - Bots with news feeds: <5 second response time
- **Data Source:** WebSocket RTDS for comments and external price data

---

## 2. Profitable Bot Identification

### 2.1 Performance Metrics

#### Win Rate Analysis
- **Data Collection:**
  - Query Polymarket Subgraph for historical positions by address
  - Track resolved markets and payout outcomes
  - Calculate realized PnL: `(final_price - entry_price) * position_size`
- **Profitability Threshold:**
  - Win rate > 55% (above random chance + fees)
  - Sharpe ratio > 1.5
  - Minimum sample size: 50 trades

#### Volume & Activity Threshold
- **Filters:**
  - Minimum trading volume: $10,000/week
  - Active on >20 unique markets
  - Consistent activity over >30 days
- **Rationale:** Small bots may be experimental; high-volume indicates operational strategy

#### Risk-Adjusted Returns
- **Metrics to Calculate:**
  - Sharpe Ratio: `(mean_return - risk_free_rate) / std_dev_return`
  - Maximum drawdown
  - Profit factor: `gross_profit / gross_loss`
- **Target Profile:** Sharpe > 2.0, Max DD < 20%

### 2.2 Bot Classification System

#### Market Maker Bots
- **Characteristics:**
  - High order count, low fill rate
  - Tight spreads, both sides of book
  - Profit from bid-ask spread + maker rebates
- **Profitability:** Moderate (1-3% annual), low risk
- **Mirroring Value:** Low (latency-sensitive, hard to front-run)

#### Information Trader Bots
- **Characteristics:**
  - Large directional trades
  - Rapid response to news/events
  - High win rate on resolved markets
- **Profitability:** High (10-30%+ on winning trades)
- **Mirroring Value:** **HIGH** - These are the primary target

#### Arbitrage Bots
- **Characteristics:**
  - Simultaneous trades across related markets
  - Delta-neutral positions
  - Exploits mispricing between correlated outcomes
- **Profitability:** Moderate-High (5-15%)
- **Mirroring Value:** Medium (requires fast execution)

#### Statistical Arbitrage
- **Characteristics:**
  - Mean-reversion strategies
  - Pairs trading across similar markets
  - High frequency position turnover
- **Profitability:** Moderate (3-8%)
- **Mirroring Value:** Medium-Low (requires quant modeling)

### 2.3 Bot Ranking System

**Score Components (0-100 scale):**

1. **Historical Performance (40%)**
   - Win rate on resolved markets
   - Risk-adjusted returns (Sharpe)
   - Consistency across market types

2. **Signal Quality (30%)**
   - Lead time before major price moves
   - Correlation with eventual resolution
   - False positive rate

3. **Trading Volume (20%)**
   - Sufficient liquidity to mirror
   - Position size relative to market depth
   - Impact on market price

4. **Operational Consistency (10%)**
   - Uptime and activity frequency
   - Strategy stability over time
   - Lack of recent performance degradation

**Ranking Tiers:**
- **Tier 1 (Score 80-100):** Primary mirroring targets - information traders with strong track record
- **Tier 2 (Score 60-79):** Secondary targets - reliable but lower alpha
- **Tier 3 (Score 40-59):** Watchlist - monitor for improvements
- **Tier 4 (<40):** Ignore - insufficient edge or unreliable

---

## 3. Mirroring Strategy Design

### 3.1 Core Strategy: Latency Arbitrage

**Concept:** Detect bot entry signals and immediately place similar orders before market fully reacts.

#### Execution Flow
1. **Signal Detection** (Target: <50ms)
   - WebSocket receives `last_trade_price` event
   - Identify if trade originates from Tier 1/2 bot address
   - Analyze trade size, direction, and market context

2. **Trade Decision** (Target: <100ms total)
   - Check if trade size exceeds threshold ($500+ for liquid markets)
   - Verify market has sufficient remaining liquidity
   - Confirm bot historical accuracy on this market type

3. **Order Placement** (Target: <200ms total)
   - Place limit order at same or slightly better price
   - Size order proportionally to bot trade (e.g., 30-50% of bot size)
   - Set GTC (Good-Til-Canceled) with 5-minute TTL

4. **Position Management**
   - Monitor market movement over next 15-60 minutes
   - Scale out if price moves favorably (>2% profit)
   - Exit at break-even if no movement after 4 hours
   - Stop loss at -5% or if bot reverses position

### 3.2 Mirror Sizing Algorithm

```python
def calculate_mirror_size(bot_trade):
    """
    Dynamically size mirror trades based on bot reliability and market conditions
    """
    base_size = min(bot_trade.size * 0.4, MAX_POSITION_SIZE)
    
    # Adjust for bot tier
    tier_multiplier = {1: 1.0, 2: 0.6, 3: 0.3}
    size = base_size * tier_multiplier[bot_trade.bot_tier]
    
    # Adjust for market liquidity
    orderbook_depth = get_orderbook_depth(bot_trade.token_id)
    if orderbook_depth < size * 2:
        size *= 0.5  # Reduce size in thin markets
    
    # Adjust for bot conviction (size relative to typical)
    if bot_trade.size > bot_trade.avg_size * 2:
        size *= 1.3  # Bot is trading larger than usual
    
    return round(size, 2)
```

### 3.3 Risk Management Framework

#### Per-Trade Limits
- Maximum single trade: $1,000
- Maximum position per market: $5,000
- Stop loss: -5% per trade
- Profit target: +15% (scale out in increments)

#### Portfolio Limits
- Maximum total exposure: $50,000
- Maximum correlated exposure: $15,000 (e.g., all election markets)
- Daily loss limit: -$2,000 (pause trading)
- Maximum open positions: 20 concurrent trades

#### Bot-Specific Limits
- If Tier 1 bot has 3 consecutive losses → downgrade to Tier 2
- If any bot shows sustained underperformance (win rate <50% over 30 days) → remove from mirror list
- Review and rebalance bot rankings weekly

### 3.4 Exit Strategy

**Time-Based Exits:**
- If no price movement after 4 hours → exit at best available price
- Close all positions 24 hours before market resolution (avoid resolution risk)

**Signal-Based Exits:**
- If mirrored bot reverses position → immediately exit mirror trade
- If market moves against position by >3% with high volume → exit 50% of position
- If new Tier 1 bot takes opposite position → exit and potentially reverse

**Profit-Taking:**
- Target 1 (2% profit): Take 30% of position off
- Target 2 (5% profit): Take additional 40% off
- Target 3 (10%+ profit): Close remaining 30%

---

## 4. Data Infrastructure Requirements

### 4.1 Real-Time Data Streams

#### Primary: Polymarket WebSocket (CLOB)
- **Endpoint:** `wss://ws-subscriptions.polymarket.com/ws/subscriptions`
- **Channels to Subscribe:**
  1. `market` channel: For orderbook updates and trade executions
     - `last_trade_price`: Track all trades with address attribution
     - `price_change`: Monitor orderbook liquidity changes
     - `book`: Full orderbook snapshots
  2. `user` channel (authenticated): For order confirmations and fills

- **Implementation:**
  ```python
  import websocket
  import json
  
  def on_message(ws, message):
      data = json.loads(message)
      
      if data['event_type'] == 'last_trade_price':
          trader_address = extract_address_from_trade(data)
          if trader_address in tier1_bots:
              trigger_mirror_signal(data)
  
  ws = websocket.WebSocketApp(
      "wss://ws-subscriptions.polymarket.com/ws/subscriptions",
      on_message=on_message
  )
  ```

#### Secondary: Real-Time Data Socket (RTDS)
- **Endpoint:** `wss://ws-live-data.polymarket.com`
- **Use Cases:**
  - Monitor comment activity for sentiment shifts
  - Track crypto price feeds for correlated markets
  - Detect news events that might trigger bot activity

### 4.2 Historical Data Collection

#### Polymarket Subgraph (GraphQL)
- **Purpose:** Historical position data, resolved market outcomes, user statistics
- **Endpoint:** Via Goldsky/The Graph
- **Key Queries:**
  ```graphql
  query BotPerformance($address: String!, $minTimestamp: Int!) {
    positions(where: {user: $address, createTimestamp_gte: $minTimestamp}) {
      market {
        id
        question
        resolved
        winningOutcome
      }
      outcomeIndex
      quantityBought
      quantitySold
      netQuantity
      avgBuyPrice
      avgSellPrice
      realizedPnL
    }
  }
  ```

#### Blockchain Data Providers
- **Goldsky:** Real-time Polymarket trade stream to data warehouse
  - Setup: Streaming pipeline to PostgreSQL/ClickHouse
  - Use: Historical trade analysis, backtesting
  
- **Dune Analytics:** Ad-hoc SQL queries for pattern discovery
  - Use: Initial bot discovery, performance validation
  - Key tables: `polymarket.trades`, `polymarket.positions`

- **CryptoHouse (ClickHouse):** Fast SQL queries on Polymarket data
  - Use: Real-time analytics, bot classification

### 4.3 Data Storage Architecture

#### Hot Storage (Real-Time Processing)
- **Technology:** Redis/KeyDB
- **Purpose:** 
  - Live orderbook state (L2 data)
  - Active bot tracking (current positions, recent trades)
  - Mirror trade queue and execution status
- **TTL:** 24-48 hours
- **Size Estimate:** ~5 GB for 100 active markets

#### Warm Storage (Recent History)
- **Technology:** PostgreSQL with TimescaleDB extension
- **Schema:**
  ```sql
  -- Trades table
  CREATE TABLE trades (
      id SERIAL PRIMARY KEY,
      timestamp TIMESTAMPTZ NOT NULL,
      token_id VARCHAR(100),
      market_id VARCHAR(100),
      trader_address VARCHAR(100),
      side VARCHAR(10),  -- BUY/SELL
      price DECIMAL(10,6),
      size DECIMAL(18,6),
      is_maker BOOLEAN,
      bot_tier INT,  -- NULL if not identified bot
      INDEX idx_trader_time (trader_address, timestamp),
      INDEX idx_market_time (market_id, timestamp)
  );
  
  -- Bot performance tracking
  CREATE TABLE bot_performance (
      address VARCHAR(100) PRIMARY KEY,
      total_trades INT,
      win_rate DECIMAL(5,4),
      sharpe_ratio DECIMAL(5,2),
      total_pnl DECIMAL(18,2),
      current_tier INT,
      last_updated TIMESTAMPTZ
  );
  ```
- **Retention:** 90 days of detailed data
- **Size Estimate:** ~50 GB for 90 days

#### Cold Storage (Historical Archive)
- **Technology:** S3/Object storage with Parquet format
- **Purpose:** Long-term backtesting, compliance, research
- **Retention:** Indefinite
- **Compression:** ~1 GB per month of compressed trade data

### 4.4 Compute Requirements

#### Real-Time Processing Server
- **Specs:** 8-16 CPU cores, 32 GB RAM, SSD storage
- **Purpose:** WebSocket processing, signal detection, order execution
- **Latency Target:** <50ms p99 for signal detection
- **OS:** Linux (Ubuntu 22.04 LTS)
- **Location:** AWS us-east-1 or GCP us-central1 (low latency to Polygon RPC)

#### Analytics Server
- **Specs:** 16-32 CPU cores, 128 GB RAM
- **Purpose:** Historical analysis, bot classification, backtesting
- **Technology Stack:**
  - Python 3.9+ (pandas, numpy, scikit-learn)
  - PostgreSQL + TimescaleDB
  - Jupyter notebooks for research

#### Trading Infrastructure
- **Polymarket CLOB Client:** py-clob-client (Python) or clob-client (TypeScript)
- **RPC Provider:** Alchemy or QuickNode (Polygon mainnet)
  - Requirement: Low-latency, high-throughput plan
  - Failover: Secondary RPC endpoint
- **Wallet Management:** Secure key storage (AWS KMS or hardware wallet)

---

## 5. Implementation Roadmap

### Phase 1: Data Collection & Bot Discovery (Weeks 1-3)

**Week 1: Infrastructure Setup**
- [ ] Deploy PostgreSQL + TimescaleDB database
- [ ] Set up WebSocket listener for Polymarket CLOB
- [ ] Configure Redis for real-time state management
- [ ] Establish Goldsky/Dune access for historical data

**Week 2: Historical Data Analysis**
- [ ] Download 6 months of trade history from Dune/subgraph
- [ ] Build bot detection algorithms (timing, sizing, patterns)
- [ ] Identify initial cohort of 50-100 potential bot addresses
- [ ] Calculate basic performance metrics (win rate, volume, activity)

**Week 3: Bot Classification**
- [ ] Implement bot scoring system
- [ ] Classify bots by strategy type (market maker, info trader, arb)
- [ ] Create Tier 1/2/3 bot lists (top 20-30 bots)
- [ ] Validate performance on recent resolved markets

**Deliverables:**
- List of 20-30 high-performing bot addresses with tier classification
- Database populated with 6 months of historical data
- Initial bot performance dashboard

### Phase 2: Strategy Development & Backtesting (Weeks 4-6)

**Week 4: Mirror Strategy Implementation**
- [ ] Build mirror trade logic (signal detection → order placement)
- [ ] Implement sizing algorithm and risk management rules
- [ ] Create simulation environment for backtesting
- [ ] Develop order execution module (using py-clob-client)

**Week 5: Backtesting**
- [ ] Run backtest on previous 3 months of data
- [ ] Test various mirror ratios (20%, 30%, 50% of bot size)
- [ ] Optimize entry/exit timing and profit targets
- [ ] Analyze slippage and execution assumptions

**Week 6: Strategy Refinement**
- [ ] Incorporate backtest learnings into strategy
- [ ] Stress test under different market conditions
- [ ] Build risk monitoring and alerting system
- [ ] Create paper trading simulation

**Deliverables:**
- Backtested results report (expected returns, Sharpe, max drawdown)
- Optimized strategy parameters
- Paper trading system ready for live data testing

### Phase 3: Paper Trading (Weeks 7-8)

**Week 7-8: Live Paper Trading**
- [ ] Connect to live WebSocket feeds
- [ ] Run mirror strategy in paper trading mode (no real orders)
- [ ] Log all hypothetical trades with timestamps
- [ ] Monitor signal quality and execution latency
- [ ] Compare paper results to backtest expectations

**Success Criteria:**
- Paper trading performance within 20% of backtest expectations
- Average signal-to-order latency <200ms
- >80% order fill rate in simulation
- Risk management triggers functioning correctly

**Deliverables:**
- 2-week paper trading performance report
- Identified gaps between backtest and live conditions
- Refined strategy with live market insights

### Phase 4: Live Trading Pilot (Weeks 9-12)

**Week 9: Small-Scale Launch**
- [ ] Deploy trading capital: $5,000-$10,000 initial
- [ ] Set conservative position limits (max $500 per trade)
- [ ] Monitor all trades manually for first 3 days
- [ ] Implement automated daily performance reporting

**Week 10-11: Monitoring & Optimization**
- [ ] Track live performance vs. paper trading
- [ ] Adjust bot tiers based on real-world results
- [ ] Fine-tune risk parameters (position sizing, stop losses)
- [ ] Expand to additional bot cohorts if successful

**Week 12: Scale Decision**
- [ ] Evaluate 4-week pilot results
- [ ] Decision: Scale up, optimize further, or pivot
- [ ] If successful: Increase capital to $25,000-$50,000
- [ ] Document lessons learned and edge sources

**Go/No-Go Criteria:**
- Sharpe ratio > 1.0 over 4 weeks
- Positive returns after fees
- Maximum drawdown < 15%
- No critical system failures or execution issues

**Deliverables:**
- Live trading performance report
- Updated bot rankings based on live mirror results
- Scaling plan or pivot recommendations

### Phase 5: Scaling & Automation (Month 4+)

**Ongoing Activities:**
- Weekly bot performance reviews and tier adjustments
- Monthly strategy backtests with new data
- Continuous monitoring for market regime changes
- Expansion to additional sophisticated bots as discovered

**Optimization Priorities:**
1. Reduce latency (target <100ms end-to-end)
2. Improve bot classification accuracy (ML models)
3. Develop proprietary alpha signals (not just mirroring)
4. Explore cross-market arbitrage opportunities

---

## 6. Expected Performance & Economics

### 6.1 Performance Projections

#### Conservative Scenario (Base Case)
- **Annual Return:** +8-12%
- **Sharpe Ratio:** 1.2-1.5
- **Win Rate:** 52-55%
- **Maximum Drawdown:** 15-20%
- **Assumptions:**
  - Mirror 20-30 Tier 1/2 bots
  - 3-5 trades per day on average
  - Capture 40-60% of bot alpha after slippage/fees

#### Moderate Scenario (Target)
- **Annual Return:** +15-25%
- **Sharpe Ratio:** 1.8-2.2
- **Win Rate:** 56-60%
- **Maximum Drawdown:** 12-18%
- **Assumptions:**
  - Successful identification of top 10 information trader bots
  - Low-latency execution (<150ms average)
  - Effective risk management and position sizing

#### Optimistic Scenario (Upside)
- **Annual Return:** +30-50%
- **Sharpe Ratio:** 2.5-3.0
- **Win Rate:** 62-68%
- **Maximum Drawdown:** 10-15%
- **Assumptions:**
  - Exclusive access to highest-alpha bots before broader discovery
  - Development of proprietary enhancements to mirror strategy
  - Favorable market conditions (high volatility, frequent mispricings)

### 6.2 Edge Sources & Durability

#### Primary Edge Sources

1. **Information Asymmetry (50% of edge)**
   - Bots have superior information processing (news, on-chain data)
   - Mirroring captures this before market fully adjusts
   - **Durability:** Medium (6-18 months) - edge degrades as bots become known

2. **Execution Speed (30% of edge)**
   - Sub-second response to bot signals
   - Capture liquidity before wider market reacts
   - **Durability:** High (18-36 months) - requires infrastructure to compete

3. **Selection Skill (20% of edge)**
   - Identifying truly profitable bots vs. lucky traders
   - Dynamic tier adjustments based on changing performance
   - **Durability:** High (24-48 months) - proprietary bot scoring system

#### Edge Decay Mitigation

- **Continuous Discovery:** Regularly scan for new profitable bots
- **Strategy Evolution:** Develop proprietary signals beyond pure mirroring
- **Market Expansion:** Apply learnings to new prediction markets as they launch
- **Alpha Stacking:** Layer multiple uncorrelated strategies

### 6.3 Cost Structure

#### Trading Costs
- **Polymarket Fees:**
  - Maker: -0.00% (rebate on some markets, net zero)
  - Taker: 0.00% (no fee currently)
  - *Note: Fee structure may change; assume 5-10 bps blended*
  
- **Slippage:** 
  - Estimated 10-20 bps per trade in liquid markets
  - Higher (50+ bps) in thin markets → avoid or size down

- **Gas Fees (Polygon):**
  - ~$0.01-0.05 per transaction
  - Negligible relative to trade sizes ($500+)

**Total Trading Costs:** ~15-30 bps per round-trip trade

#### Infrastructure Costs (Monthly)
- Server hosting (AWS/GCP): $500-1,000
- RPC provider (Alchemy/QuickNode): $200-500
- Database (managed PostgreSQL): $100-300
- Data feeds (Goldsky, if used): $0-500
- **Total:** ~$800-2,300/month = ~$10,000-28,000/year

#### Break-Even Analysis
- At $50,000 capital: Need >2% annual return to cover costs
- At $250,000 capital: Infrastructure costs are <1.2% drag
- **Optimal Scale:** $100,000-$500,000 for cost efficiency

### 6.4 Scalability Limits

#### Capacity Constraints
1. **Market Liquidity:**
   - Polymarket daily volume: ~$10-50M across all markets
   - Can realistically capture 0.1-0.5% of volume without impact
   - **Effective Capacity:** $2-5M in active capital before hitting limits

2. **Signal Decay:**
   - As more traders mirror the same bots, edge diminishes
   - Estimated sustainable AUM: $1-3M before significant alpha decay

3. **Execution Quality:**
   - Slippage increases with position size
   - Recommend max 2-5% of daily market volume per trade

#### Scaling Strategy
- **Phase 1 (Months 1-6):** $10,000-$50,000 → Prove edge
- **Phase 2 (Months 7-12):** $50,000-$250,000 → Optimize execution
- **Phase 3 (Year 2+):** $250,000-$1,000,000 → Diversify strategies
- **Beyond $1M:** Develop proprietary alpha, move beyond pure mirroring

---

## 7. Risks & Mitigations

### 7.1 Strategy Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Bot changes strategy | High | Medium | Track multiple bots; diversify |
| Bot is front-run by others | Medium | Medium | Optimize latency; be first |
| Mirroring becomes crowded | High | Low-Medium | Proprietary bot discovery |
| Market manipulation by bot | High | Low | Validate bot trades against orderbook |

### 7.2 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| WebSocket disconnection | High | Low | Automatic reconnection; redundant feeds |
| RPC provider downtime | High | Low | Multi-provider failover |
| Execution latency spikes | Medium | Medium | Monitor p99 latency; alerts |
| Database corruption | Medium | Very Low | Automated backups; replication |

### 7.3 Market Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Polymarket volume decline | High | Low | Diversify to other prediction markets |
| Regulatory changes | High | Low-Medium | Monitor regulatory environment |
| Smart contract exploit | Very High | Very Low | Limit capital at risk; insurance if available |
| Fee structure changes | Medium | Medium | Model breakeven under higher fees |

---

## 8. Monitoring & KPIs

### 8.1 Daily Metrics

- **Signal Quality:**
  - Number of bot trades detected
  - Number of mirror trades executed
  - Fill rate (executed / attempted)
  
- **Performance:**
  - Daily PnL (realized + unrealized)
  - Win rate on closed positions
  - Average profit per winning trade
  - Average loss per losing trade

- **Execution:**
  - Average signal-to-order latency
  - Slippage (expected vs. actual fill price)
  - Failed orders and reasons

### 8.2 Weekly Reviews

- **Bot Performance:**
  - Update bot tier rankings
  - Identify underperforming bots (downgrade/remove)
  - Discover new potential bots (screening)

- **Risk Metrics:**
  - Current exposure by market/category
  - Maximum drawdown (current vs. historical)
  - Value at Risk (95% confidence)

### 8.3 Monthly Deep Dives

- **Strategy Analysis:**
  - Sharpe ratio and risk-adjusted returns
  - Comparison to backtest expectations
  - Breakdown of returns by bot tier and market type

- **Competitive Landscape:**
  - Are other addresses mirroring the same bots?
  - Has bot alpha degraded?
  - New opportunities or market shifts?

---

## 9. Conclusion

The Polymarket bot mirroring strategy offers a compelling risk-adjusted return opportunity by leveraging publicly observable on-chain trading patterns. By systematically identifying high-performing algorithmic traders and mirroring their positions with low latency, the strategy can capture a meaningful fraction of sophisticated bots' information edge.

### Key Success Factors
1. **Rigorous Bot Selection:** Only mirror truly profitable, consistent bots
2. **Low-Latency Execution:** Sub-200ms signal-to-order pipeline
3. **Disciplined Risk Management:** Strict position limits and stop losses
4. **Continuous Adaptation:** Regular bot re-ranking and strategy refinement

### Next Steps
1. Set up data infrastructure and begin historical bot discovery (Phase 1)
2. Backtest top bot cohort over 3-6 months of data (Phase 2)
3. Paper trade for 2-4 weeks to validate live execution (Phase 3)
4. Launch live trading pilot with $5-10K capital (Phase 4)

**Expected Timeline to Profitability:** 8-12 weeks from start to initial live trading; 4-6 months to reach target scale ($50-100K).

---

## Appendix A: Data Sources Quick Reference

| Data Type | Source | Access Method | Latency |
|-----------|--------|---------------|---------|
| Live trades | CLOB WebSocket | `wss://ws-subscriptions.polymarket.com` | ~50-200ms |
| Orderbook L2 | CLOB WebSocket | `market` channel | ~50-200ms |
| Historical trades | Goldsky/Dune | SQL queries | Batch |
| User positions | Polymarket Subgraph | GraphQL | ~1-5 min |
| Market metadata | Gamma API | REST `https://gamma-api.polymarket.com` | ~100-500ms |
| News/comments | RTDS WebSocket | `wss://ws-live-data.polymarket.com` | ~100-500ms |

## Appendix B: Code Repositories

- **py-clob-client:** https://github.com/Polymarket/py-clob-client
- **clob-client (TypeScript):** https://github.com/Polymarket/clob-client
- **Polymarket Agents:** https://github.com/Polymarket/agents
- **Polymarket Subgraph:** https://github.com/Polymarket/polymarket-subgraph

## Appendix C: Useful Queries

### Dune: Top Traders by Volume (Last 30 Days)
```sql
SELECT 
    trader_address,
    COUNT(*) as trade_count,
    SUM(size_usd) as total_volume,
    AVG(size_usd) as avg_trade_size
FROM polymarket.trades
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY trader_address
HAVING COUNT(*) > 100
ORDER BY total_volume DESC
LIMIT 100
```

### Subgraph: Bot Win Rate on Resolved Markets
```graphql
query BotWinRate($address: String!) {
  positions(
    where: {
      user: $address, 
      market_: {resolved: true}
    }
  ) {
    market {
      id
      question
      winningOutcome
    }
    outcomeIndex
    realizedPnL
  }
}
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-07  
**Maintained By:** Research Team  
**Review Frequency:** Monthly or upon significant market changes
