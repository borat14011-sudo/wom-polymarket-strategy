# Market Microstructure Analyzer for Polymarket

> Professional-grade order book analysis for Polymarket traders

## 🎯 What This Does

Analyzes market microstructure on Polymarket to give you **actionable trading insights**:

- **Spread Analysis** - Is execution cost reasonable?
- **Liquidity Metrics** - Can you trade without moving the market?
- **Whale Detection** - Where are the big players positioned?
- **Price Impact** - How much will your order cost in slippage?
- **Flow Analysis** - Which way is the momentum?
- **Smart Sizing** - What's the optimal order size?

## 🚀 Quick Start

### Installation

```bash
# No dependencies! Uses only Python standard library
python market-microstructure.py --help
```

### Basic Usage

```bash
# Analyze a specific market
python market-microstructure.py --market TOKEN_ID

# Watch whale activity
python market-microstructure.py --market TOKEN_ID --whales

# Check liquidity before trading
python market-microstructure.py --market TOKEN_ID --liquidity

# Estimate price impact for $5K order
python market-microstructure.py --market TOKEN_ID --impact 5000

# Real-time monitoring (refresh every 30s)
python market-microstructure.py --market TOKEN_ID --monitor 30
```

### Finding Token IDs

Token IDs are the contract addresses for specific outcome tokens on Polymarket.

**Method 1: From Polymarket UI**
1. Open market on Polymarket
2. Click on an outcome (Yes/No)
3. Look at URL or inspect network requests for `token_id`

**Method 2: From CLOB API**
```bash
curl "https://clob.polymarket.com/markets"
```

## 📊 Understanding the Output

### Spread Metrics
```
Mid Price: $0.5250
Spread: $0.0020 (38.1 bps)
Best Bid: $0.5240
Best Ask: $0.5260
```

**What it means:**
- **38.1 bps** - Transaction cost for immediate execution
- **<50 bps** = Good, reasonable cost to trade
- **>100 bps** = Expensive, consider limit orders

### Imbalance Metrics
```
Signal: BUY_PRESSURE
Net Pressure: +15.3%
Bid/Ask Ratio: 1.36
```

**What it means:**
- **BUY_PRESSURE** - More demand than supply
- **+15.3%** - Bullish momentum
- **1.36 ratio** - 36% more value on bid side

**Trading implication:** Price likely to move up

### Liquidity Score
```
Liquidity Score: 72.4/100
Total Liquidity: $45,230
```

**Interpretation:**
- **80-100** - Excellent, trade freely
- **60-79** - Good, suitable for most orders
- **40-59** - Fair, use limit orders
- **<40** - Poor, high slippage risk

### Price Impact
```
Price Impact (for $1K order):
  Estimated Price: $0.5265
  Slippage: 0.28%
  Optimal Order Size: $3,450
```

**What it means:**
- Your $1K order would pay $0.5265 instead of $0.5260 (mid)
- **0.28% slippage** is acceptable
- Orders up to $3,450 will have <1% slippage

### Whale Activity
```
🐋 Large Positions (>$10K): 3
Smart Money Score: 68.5/100

Top 3 Positions:
  1. BID: $15,200 @ $0.5235
  2. ASK: $12,800 @ $0.5270
  3. BID: $11,500 @ $0.5220
```

**What it means:**
- 3 whales with >$10K positions
- They're positioned intelligently (68.5/100)
- Most whale money is on the BID side (bullish)

**Trading implication:** Follow the smart money

## 💡 Professional Trading Strategies

### Strategy 1: Scalping
**Goal:** Quick profits from bid-ask spread

```bash
# Monitor every 10 seconds
python market-microstructure.py --market TOKEN_ID --monitor 10
```

**Requirements:**
- Spread < 30 bps
- Liquidity score > 70
- High refresh rate

**Profit:** 10-20 bps per trade, 50+ trades/day

---

### Strategy 2: Momentum Trading
**Goal:** Ride directional pressure

```bash
# Check flow + imbalance
python market-microstructure.py --market TOKEN_ID --flow
```

**Entry signals:**
- BUY_PRESSURE + BULLISH momentum
- Net pressure > +20%
- Whale positions aligned with momentum

**Exit signals:**
- Pressure flips to opposite side
- Reversal signals appear

---

### Strategy 3: Large Order Execution
**Goal:** Minimize slippage on big trades

```bash
# Estimate impact
python market-microstructure.py --market TOKEN_ID --impact 10000
```

**Execution plan:**
1. Check optimal size (e.g., $3,450)
2. Split order: 10000 / 3450 = 3 chunks
3. Execute slowly: 1 chunk every 5-10 minutes
4. Monitor order book between chunks

**Expected savings:** 0.5-1.5% in slippage

---

### Strategy 4: Market Making
**Goal:** Earn spread while providing liquidity

```python
from market_microstructure import MarketAnalyzer

analyzer = MarketAnalyzer(token_id)
spread = analyzer.get_spread()

# Place limit orders at optimal prices
bid_price = spread.mid_price * 0.998  # 20 bps below mid
ask_price = spread.mid_price * 1.002  # 20 bps above mid

# Only if liquidity is good
liquidity = analyzer.get_liquidity_metrics()
if liquidity.score > 60:
    # Place orders via Polymarket API
    place_bid_order(bid_price, size)
    place_ask_order(ask_price, size)
```

**Risk management:**
- Only trade liquid markets (score > 60)
- Keep position small (<5% of total liquidity)
- Cancel orders on excessive imbalance

---

## 🔧 Python Integration

### Basic Integration
```python
from market_microstructure import MarketAnalyzer

# Initialize
analyzer = MarketAnalyzer("YOUR_TOKEN_ID")

# Get current metrics
spread = analyzer.get_spread()
liquidity = analyzer.get_liquidity_metrics()
imbalance = analyzer.get_imbalance()

# Make trading decision
if liquidity.score > 70 and imbalance.signal == "BUY_PRESSURE":
    print("🟢 GO LONG")
```

### Advanced: Trading Bot
```python
import time
from market_microstructure import MarketAnalyzer

class TradingBot:
    def __init__(self, token_id):
        self.analyzer = MarketAnalyzer(token_id)
        self.position = None
    
    def analyze(self):
        """Run market analysis"""
        spread = self.analyzer.get_spread()
        imbalance = self.analyzer.get_imbalance()
        liquidity = self.analyzer.get_liquidity_metrics()
        flow = self.analyzer.analyze_flow()
        
        return {
            'quality': liquidity.score > 60 and spread.spread_bps < 100,
            'signal': flow['momentum'],
            'strength': abs(imbalance.net_pressure)
        }
    
    def execute(self):
        """Execute trading logic"""
        analysis = self.analyze()
        
        if not analysis['quality']:
            return  # Skip low-quality markets
        
        # Entry logic
        if self.position is None:
            if analysis['signal'] == 'BULLISH' and analysis['strength'] > 0.2:
                self.enter_long()
            elif analysis['signal'] == 'BEARISH' and analysis['strength'] > 0.2:
                self.enter_short()
        
        # Exit logic
        else:
            if analysis['signal'] != self.position:
                self.close_position()
    
    def run(self):
        """Main loop"""
        while True:
            try:
                self.execute()
                time.sleep(30)  # Check every 30s
            except KeyboardInterrupt:
                break

# Run the bot
bot = TradingBot("YOUR_TOKEN_ID")
bot.run()
```

### Risk Management Module
```python
from market_microstructure import MarketAnalyzer

def calculate_position_size(token_id, account_size, max_risk=0.02):
    """Calculate safe position size"""
    analyzer = MarketAnalyzer(token_id)
    
    # Get market metrics
    liquidity = analyzer.get_liquidity_metrics()
    impact = analyzer.estimate_impact(account_size * max_risk)
    
    # Safety constraints
    max_size = account_size * max_risk
    safe_size = min(
        max_size,
        liquidity.total_liquidity * 0.1,  # Max 10% of market
        impact.optimal_size  # Stay within 1% slippage
    )
    
    return safe_size

# Usage
account = 100000  # $100K
position_size = calculate_position_size("TOKEN_ID", account, max_risk=0.02)
print(f"Trade size: ${position_size:,.0f}")
```

## 📈 Example Outputs

### Full Analysis
```
======================================================================
MARKET MICROSTRUCTURE ANALYSIS - 2026-02-06T05:53:00
======================================================================

📊 SPREAD: 38.1 bps (Mid: $0.5250)
⚖️  IMBALANCE: BUY_PRESSURE (+15.3%)
💧 LIQUIDITY: 72.4/100 ($45,230 total)
💥 IMPACT: $1K order = 0.28% slippage
🐋 WHALES: 3 large positions (Smart Money: 68.5/100)
🌊 FLOW: BULLISH momentum (Strength: 15.3/100)

💡 TRADING INSIGHT:
  ✅ GOOD LIQUIDITY - Favorable conditions
  📈 Strong buying pressure - Price may move up
======================================================================
```

### Whale Report
```
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

## 🔍 API Reference

### `MarketAnalyzer`

**Constructor:**
```python
analyzer = MarketAnalyzer(token_id: str)
```

**Methods:**

- `get_spread()` → `SpreadMetrics`
  - Current bid-ask spread and depth

- `get_imbalance()` → `ImbalanceMetrics`
  - Order book imbalance and pressure

- `get_liquidity_metrics()` → `LiquidityMetrics`
  - Comprehensive liquidity analysis

- `estimate_impact(size: float, side: str)` → `PriceImpact`
  - Price impact estimation for order size

- `detect_whales()` → `WhaleActivity`
  - Large position detection and analysis

- `analyze_flow()` → `Dict`
  - Order flow and momentum indicators

- `full_analysis()` → `Dict`
  - Complete market microstructure analysis

## 🎓 For Professional Traders

### Key Metrics Cheat Sheet

| Metric | Excellent | Good | Fair | Poor |
|--------|-----------|------|------|------|
| **Spread (bps)** | <25 | 25-50 | 50-100 | >100 |
| **Liquidity Score** | 80-100 | 60-79 | 40-59 | <40 |
| **Slippage (1K)** | <0.3% | 0.3-0.7% | 0.7-1.5% | >1.5% |
| **Total Liquidity** | >$100K | $50K-$100K | $20K-$50K | <$20K |

### Trading Rules

**✅ DO:**
- Trade when liquidity score > 60
- Use limit orders when spread > 50 bps
- Split orders when impact > 1%
- Follow whale positions (if smart money score > 70)
- Monitor momentum for entry/exit timing

**❌ DON'T:**
- Trade illiquid markets (score < 40)
- Use market orders in wide spreads (>100 bps)
- Trade >10% of total market liquidity
- Ignore slippage on large orders
- Trade against strong imbalance without reason

## 🔥 Power User Tips

### 1. Multi-Market Monitoring
```bash
# Create a watchlist
for market in $(cat watchlist.txt); do
  python market-microstructure.py --market $market --json >> results.jsonl
done

# Analyze the best opportunities
cat results.jsonl | jq -s 'sort_by(.liquidity.score) | reverse | .[0:5]'
```

### 2. Alert System
```python
# Discord/Telegram alerts
from market_microstructure import MarketAnalyzer

analyzer = MarketAnalyzer(token_id)
whales = analyzer.detect_whales()

if whales.unusual_volume:
    send_alert("🚨 Unusual whale activity detected!")
```

### 3. Historical Tracking
```python
# Log snapshots for analysis
import json
import time

while True:
    analysis = analyzer.full_analysis()
    
    with open('market_data.jsonl', 'a') as f:
        f.write(json.dumps(analysis) + '\n')
    
    time.sleep(60)  # Every minute
```

### 4. Arbitrage Detection
```python
# Compare same event across markets
analyzer_a = MarketAnalyzer(token_a)
analyzer_b = MarketAnalyzer(token_b)

price_a = analyzer_a.get_spread().mid_price
price_b = analyzer_b.get_spread().mid_price

if abs(price_a + price_b - 1.0) > 0.01:
    print(f"⚠️  Arbitrage opportunity: {abs(price_a + price_b - 1.0):.2%}")
```

## 🐛 Troubleshooting

**Error: Failed to fetch order book**
- Check token ID is correct
- Verify internet connection
- API may be rate-limited (wait 30s)

**Empty order book**
- Market may have low activity
- Token ID may be incorrect
- Try a more popular market

**Slippage seems high**
- That's the reality of the market
- Split your order into smaller chunks
- Or provide liquidity instead

## 📚 Learn More

- [Polymarket CLOB API Docs](https://docs.polymarket.com)
- [Market Microstructure Theory](https://en.wikipedia.org/wiki/Market_microstructure)
- [Order Book Analysis](https://www.investopedia.com/terms/o/order-book.asp)

## 🤝 Contributing

This is a professional tool for serious traders. Contributions welcome:

- Additional metrics (VWAP, TWAP, etc.)
- Machine learning predictions
- WebSocket streaming support
- Multi-market correlation
- Backtesting framework

## ⚠️ Disclaimer

This tool is for informational purposes only. Trading involves risk. Always:
- Do your own research
- Start with small position sizes
- Use proper risk management
- Never trade more than you can afford to lose

**Not financial advice. Use at your own risk.**

---

**Great success!** 🎯

Built for professional Polymarket traders who want an edge.
