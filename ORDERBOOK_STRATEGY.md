# ORDER BOOK DEPTH STRATEGY

**Created:** 2026-02-07  
**Status:** Research Phase  
**Hypothesis:** Thin order books indicate manipulation risk; deep order books signal smart money conviction

---

## Theory & Background

### Order Book Depth as a Signal

**Core Premise:**
- **Thin order books** (low liquidity) = easier to manipulate, higher slippage risk, less conviction
- **Deep order books** (high liquidity) = harder to manipulate, institutional interest, stronger conviction

**Why This Matters:**
1. **Manipulation Resistance:** Markets with $10K+ depth within 5% of mid-price are harder to move artificially
2. **Smart Money Indicator:** Deep order books suggest institutional traders/informed money are participating
3. **Execution Quality:** Deep markets = better fills, less slippage
4. **Market Stability:** Thin books can experience violent swings from small orders

### Market Microstructure Insights

**Bid-Ask Spread vs Depth:**
- Tight spread + thin book = trap (looks good, executes poorly)
- Wide spread + deep book = institutional market (high conviction, higher fees)
- Tight spread + deep book = ideal (liquid, efficient)
- Wide spread + thin book = avoid (manipulation central)

**Order Book Imbalance:**
- Heavy bid side = buying pressure
- Heavy ask side = selling pressure
- Balanced book = fair pricing
- Sudden imbalances = potential manipulation or informed flow

---

## Proposed Strategy

### Entry Requirements

**Minimum Depth Threshold:**
- **≥$10,000 total liquidity** within 5% of mid-price (both sides combined)
- **Balanced book:** Neither side >70% of total depth (prevents one-sided manipulation)
- **Spread check:** Bid-ask spread <2% for efficiency

**Pre-Trade Checklist:**
```
1. Query CLOB order book data
2. Calculate depth within 5% range:
   - Sum all bids from mid-price down to -5%
   - Sum all asks from mid-price up to +5%
   - Total = bid_depth + ask_depth
3. If total < $10K → SKIP MARKET
4. If imbalance >70/30 → FLAG for review
5. If spread >2% → Reduce position size or skip
```

### Implementation Plan

**Phase 1: API Integration**
- [ ] Identify CLOB platforms (Polymarket, dYdX, Hyperliquid, etc.)
- [ ] Test API endpoints for real-time order book data
- [ ] Build depth calculation function
- [ ] Set up monitoring dashboard

**Phase 2: Data Collection**
- [ ] Capture order book snapshots at entry time
- [ ] Log: market_id, timestamp, bid_depth, ask_depth, spread, total_depth
- [ ] Store in database for backtesting

**Phase 3: Backtesting**
- [ ] Compare outcomes: thin-book trades vs deep-book trades
- [ ] Metrics: win rate, avg profit, max drawdown, slippage
- [ ] Hypothesis test: Did thin-book markets underperform?

---

## Data Sources & Availability

### CLOB Platforms with API Access

**Polymarket (Prediction Markets):**
- API: Yes (CLOB API available)
- Real-time order books: Yes
- Historical snapshots: **Unknown** (need to verify)
- Endpoint example: `/order-book?market=<id>`

**Hyperliquid (Crypto Perps):**
- API: Yes (public WebSocket & REST)
- Historical data: Limited (recent snapshots only, not full historical)

**dYdX (Crypto Derivatives):**
- API: Yes (v4 has full CLOB data)
- Historical: Limited depth data, mostly trades

**Binance/Coinbase (CEX):**
- Order book APIs: Yes (real-time)
- Historical depth: **Not publicly available** (snapshots only via paid providers)

### Historical Order Book Data Challenge

**Problem:** Most platforms don't store historical order book depth
- Order books change every millisecond
- Storage is expensive (terabytes of data)
- Platforms typically store trades, not full book snapshots

**Solutions:**
1. **Collect forward:** Start logging order book depth now for future analysis
2. **Proxy metrics:** Use trading volume, bid-ask spread, market cap as proxies
3. **Paid services:** Kaiko, CryptoCompare, CoinMetrics (enterprise data)
4. **On-chain analysis:** For DEXs, reconstruct liquidity from blockchain data

---

## Testing Plan

### Hypothesis: Thin-Book Markets Underperform

**Test Design:**
1. **Cohort A:** Trades entered in markets with depth >$10K
2. **Cohort B:** Trades entered in markets with depth <$10K
3. **Metrics:**
   - Win rate (% profitable trades)
   - Average profit per trade
   - Slippage (expected vs actual fill price)
   - Max drawdown
   - Sharpe ratio

**Expected Outcome:**
- Cohort A (deep books) should show:
  - Higher win rate (less manipulation)
  - Lower slippage (better execution)
  - More stable returns (less volatility)

**Data Requirements:**
- At least 50 trades per cohort for statistical significance
- Control for: market type, position size, holding period
- Track: entry depth, exit depth, price impact

### Proxy Test (If Historical Data Unavailable)

**Alternative Approach:**
1. Compare **current** order book depth to **past performance**
2. For each past trade, check if the market *currently* has thin/deep book
3. Assumption: Markets with consistently thin books likely had thin books historically
4. This is imperfect but better than nothing

**Proxy Metrics:**
- 24h trading volume (high volume ≈ deeper books)
- Market cap / TVL (larger markets = more liquidity)
- Bid-ask spread history (if available)

---

## Implementation Code Sketch

```python
def check_order_book_depth(market_id, api_client):
    """
    Check if market meets minimum depth requirements
    """
    # Fetch order book
    book = api_client.get_order_book(market_id)
    
    mid_price = (book['best_bid'] + book['best_ask']) / 2
    
    # Calculate depth within 5% range
    bid_depth = sum(
        order['size'] * order['price'] 
        for order in book['bids'] 
        if order['price'] >= mid_price * 0.95
    )
    
    ask_depth = sum(
        order['size'] * order['price'] 
        for order in book['asks'] 
        if order['price'] <= mid_price * 1.05
    )
    
    total_depth = bid_depth + ask_depth
    imbalance = bid_depth / total_depth if total_depth > 0 else 0.5
    spread = (book['best_ask'] - book['best_bid']) / mid_price
    
    # Decision logic
    if total_depth < 10000:
        return {
            'approved': False,
            'reason': 'Insufficient depth',
            'depth': total_depth
        }
    
    if imbalance > 0.7 or imbalance < 0.3:
        return {
            'approved': False,
            'reason': 'Order book imbalance',
            'imbalance': imbalance
        }
    
    if spread > 0.02:
        return {
            'approved': False,
            'reason': 'Spread too wide',
            'spread': spread
        }
    
    return {
        'approved': True,
        'depth': total_depth,
        'imbalance': imbalance,
        'spread': spread
    }
```

---

## Next Steps

### Immediate Actions
1. **Verify API Access:** Test Polymarket CLOB API for order book data
2. **Build Depth Monitor:** Create script to log order book depth for all active markets
3. **Start Data Collection:** Begin capturing snapshots immediately (can't backtest without data)

### Research Questions
- [ ] Can we access Polymarket historical order book snapshots?
- [ ] What's the typical depth distribution across prediction markets?
- [ ] Is $10K the right threshold, or should it scale with market size?
- [ ] Should we weight recent depth more than stale orders far from mid?

### Validation Needed
- [ ] Backtest on available data (even limited historical)
- [ ] Paper trade with depth filter vs without for 2 weeks
- [ ] Measure: Did we avoid any major losses by skipping thin markets?

---

## Risks & Limitations

**False Negatives:**
- Good opportunities in thin markets (early mover advantage)
- Small-cap gems that haven't attracted liquidity yet

**False Positives:**
- Deep books don't guarantee correct pricing
- Institutional money can be wrong too

**Data Challenges:**
- Real-time depth changes constantly (snapshot timing matters)
- "Fake depth" (spoofing) - orders that disappear when approached
- Iceberg orders (hidden liquidity not visible in book)

**Operational Overhead:**
- Extra API calls before each trade
- Slower execution (depth check adds latency)
- Possible API rate limits

---

## Conclusion

Order book depth is a **valid and important signal** for trade quality, but:
1. **Not sufficient alone** - needs to be combined with fundamental analysis
2. **Data availability is limited** - historical testing will be challenging
3. **Forward-looking approach** - start collecting data now for future validation
4. **Adaptive thresholds** - $10K may need adjustment based on market size

**Recommendation:** Implement as a **filter, not a primary signal**. Use depth to avoid bad trades (thin, manipulated markets) rather than to find good trades. Combine with existing edge/conviction analysis.

**Status:** Ready to implement Phase 1 (API integration). Historical backtest blocked on data availability - suggest forward testing starting immediately.
