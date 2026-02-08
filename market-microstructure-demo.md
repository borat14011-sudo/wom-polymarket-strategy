# Market Microstructure Analyzer - Demo Output

## Example Analysis for a Polymarket Market

```bash
$ python market-microstructure.py --market 0x1234567890abcdef
```

### Output:

```
======================================================================
MARKET MICROSTRUCTURE ANALYSIS - 2026-02-06T05:53:00.000000
Market ID: 0x1234567890abcdef
======================================================================

📊 SPREAD METRICS:
  Mid Price: $0.5250
  Spread: $0.0020 (38.1 bps)
  Best Bid: $0.5240
  Best Ask: $0.5260

⚖️  ORDER BOOK IMBALANCE:
  Signal: BUY_PRESSURE
  Net Pressure: +15.3%
  Bid/Ask Ratio: 1.36

💧 LIQUIDITY METRICS:
  Liquidity Score: 72.4/100
  Total Liquidity: $45,230
  Bid Liquidity: $26,500
  Ask Liquidity: $18,730
  Resilience: 68.2%

💥 PRICE IMPACT (for $1K order):
  Estimated Price: $0.5265
  Slippage: 0.28%
  Optimal Order Size (<1% slippage): $3,450

🐋 WHALE ACTIVITY:
  Large Positions (>$10K): 3
  Smart Money Score: 68.5/100
  Unusual Volume: No

  Top 3 Positions:
    1. BID: $15,200 @ $0.5235
    2. ASK: $12,800 @ $0.5270
    3. BID: $11,500 @ $0.5220

🌊 FLOW ANALYSIS:
  Momentum: BULLISH
  Flow Strength: 15.3/100
  
💡 TRADING INSIGHT:
  ✅ GOOD LIQUIDITY - Favorable trading conditions
  📈 Strong buying pressure - Price may move up

======================================================================
```

## Advanced Usage Examples

### 1. Whale Monitoring
```bash
$ python market-microstructure.py --market 0x1234... --whales

🐋 WHALE ACTIVITY REPORT

Large Positions (>$10K): 5
Smart Money Score: 73.2/100
Unusual Volume: False

Top 10 Positions:
 1. BID  $   25,400 @ $0.5230
 2. ASK  $   18,600 @ $0.5280
 3. BID  $   15,200 @ $0.5235
 4. BID  $   12,800 @ $0.5220
 5. ASK  $   11,900 @ $0.5290
```

### 2. Liquidity Assessment
```bash
$ python market-microstructure.py --market 0x1234... --liquidity

💧 LIQUIDITY REPORT

Liquidity Score: 78.6/100
Total Liquidity: $67,840
  Bid Side: $38,200
  Ask Side: $29,640
Concentration: 0.124 (lower = better)
Resilience: 71.5%
```

### 3. Price Impact Analysis
```bash
$ python market-microstructure.py --market 0x1234... --impact 5000

💥 PRICE IMPACT ANALYSIS ($5,000 order)

Estimated Fill Price: $0.5282
Slippage: 0.61% ($0.0032)
Optimal Size (<1% slippage): $3,450

# Analysis: A $5K order would move the price by 0.61%
# Recommendation: Split into 2x $2.5K orders for better execution
```

### 4. Flow Analysis
```bash
$ python market-microstructure.py --market 0x1234... --flow

🌊 FLOW ANALYSIS

Momentum: BULLISH
Net Pressure: +18.5%
Signal: BUY_PRESSURE
Flow Strength: 18.5/100
```

### 5. Real-Time Monitoring
```bash
$ python market-microstructure.py --market 0x1234... --monitor 30

📡 Monitoring market 0x1234... (refresh every 30s)
Press Ctrl+C to stop

# Updates every 30 seconds with full analysis
# Perfect for active trading sessions
```

### 6. JSON Output (for integration)
```bash
$ python market-microstructure.py --market 0x1234... --json

{
  "timestamp": "2026-02-06T05:53:00.000000",
  "market_id": "0x1234567890abcdef",
  "spread": {
    "spread_abs": 0.002,
    "spread_bps": 38.1,
    "mid_price": 0.525,
    "best_bid": 0.524,
    "best_ask": 0.526
  },
  "imbalance": {
    "ratio": 1.36,
    "net_pressure": 0.153,
    "signal": "BUY_PRESSURE"
  },
  ...
}
```

## Python Integration API

```python
from market_microstructure import MarketAnalyzer

# Initialize analyzer
analyzer = MarketAnalyzer("0x1234567890abcdef")

# Get current spread
spread = analyzer.get_spread()
print(f"Current spread: {spread.spread_bps:.1f} bps")

# Estimate price impact
impact = analyzer.estimate_impact(1000)  # $1K order
print(f"$1K order slippage: {impact.slippage_pct:.2f}%")

# Detect whale activity
whales = analyzer.detect_whales()
print(f"Large positions: {len(whales.large_positions)}")
print(f"Smart money score: {whales.smart_money_score:.1f}/100")

# Get liquidity metrics
liquidity = analyzer.get_liquidity_metrics()
print(f"Liquidity score: {liquidity.score:.1f}/100")

# Analyze order book imbalance
imbalance = analyzer.get_imbalance()
print(f"Market signal: {imbalance.signal}")
print(f"Net pressure: {imbalance.net_pressure:+.2%}")

# Full microstructure analysis
analysis = analyzer.full_analysis()

# Monitor in a loop
import time
while True:
    analyzer.refresh_order_book()
    
    # Check for trading opportunities
    if liquidity.score > 70 and abs(imbalance.net_pressure) > 0.2:
        print("🎯 Trading opportunity detected!")
    
    time.sleep(30)
```

## Professional Trading Insights

### What This Tool Tells You:

1. **Spread Analysis** → Cost of immediate execution
2. **Imbalance Metrics** → Direction of pressure (bullish/bearish)
3. **Liquidity Score** → How safe is it to trade here?
4. **Price Impact** → How much will your order move the price?
5. **Whale Detection** → Are smart money players active?
6. **Flow Analysis** → Momentum and reversal signals
7. **Optimal Sizing** → What's the max order size before significant slippage?

### Key Metrics Explained:

**Spread (bps)**
- <25 bps: Excellent, tight market
- 25-50 bps: Good, reasonable cost
- 50-100 bps: Fair, watch for slippage
- >100 bps: Poor, high transaction cost

**Liquidity Score (0-100)**
- 80-100: Excellent depth, low slippage risk
- 60-79: Good, suitable for most trades
- 40-59: Fair, use limit orders
- <40: Poor, high slippage risk

**Net Pressure**
- >+20%: Strong buy pressure (bullish)
- -20% to +20%: Balanced
- <-20%: Strong sell pressure (bearish)

**Smart Money Score (0-100)**
- >70: Sophisticated positioning, follow the whales
- 50-70: Mixed signals
- <50: Less informed positioning

### Trading Strategies:

**Scalping** (high frequency, small profits)
- Need: Spread <30 bps, Liquidity >70
- Check: Every 5-10 seconds
- Tool: `--monitor 5`

**Swing Trading** (hold hours/days)
- Need: Flow analysis, whale detection
- Check: Every 15-30 minutes
- Tool: `--flow --whales`

**Large Orders** (>$5K)
- Need: Price impact analysis
- Strategy: Split orders if slippage >1%
- Tool: `--impact 5000`

**Market Making**
- Need: Real-time spread + depth monitoring
- Strategy: Place orders at optimal levels
- Tool: `--monitor 10 --json` (feed to bot)

### Integration with Trading Bots:

```python
# Example: Automated market maker
from market_microstructure import MarketAnalyzer

def should_place_orders(market_id):
    analyzer = MarketAnalyzer(market_id)
    spread = analyzer.get_spread()
    liquidity = analyzer.get_liquidity_metrics()
    
    # Only place orders in liquid, efficient markets
    return (
        spread.spread_bps < 50 and
        liquidity.score > 60 and
        liquidity.total_liquidity > 10000
    )

# Example: Smart order router
def optimal_order_execution(market_id, size_usd):
    analyzer = MarketAnalyzer(market_id)
    impact = analyzer.estimate_impact(size_usd)
    
    if impact.slippage_pct > 1.0:
        # Split order into chunks
        chunk_size = impact.optimal_size
        num_chunks = int(size_usd / chunk_size) + 1
        return f"Split into {num_chunks} orders of ${chunk_size:.0f}"
    else:
        return "Execute as single order"
```

## API Endpoints Used

**Polymarket CLOB API:**
- `GET /book?token_id={id}` - Order book snapshot
- `GET /markets/{id}` - Market information
- `GET /trades?market={id}` - Recent trade history
- `GET /price?token_id={id}` - Current price

**Rate Limits:** Respect API rate limits, use monitoring mode sparingly

## Performance Notes

- Order book snapshot: ~100-200ms
- Full analysis: ~500ms-1s
- Monitoring mode: Runs every N seconds (default 30s)
- Memory: ~50MB for 100 snapshots history

## Future Enhancements

- [ ] Historical spread analysis (best trading hours)
- [ ] Arbitrage detection across multiple markets
- [ ] Machine learning for whale behavior prediction
- [ ] WebSocket streaming for real-time updates
- [ ] Multi-market correlation analysis
- [ ] Automated alert system (Discord/Telegram)

---

**Great success! 🎯**
