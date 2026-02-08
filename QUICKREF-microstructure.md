# Market Microstructure Analyzer - Quick Reference Card

## 🚀 Essential Commands

```bash
# Full market analysis
python market-microstructure.py --market TOKEN_ID

# Whale activity
python market-microstructure.py --market TOKEN_ID --whales

# Liquidity check
python market-microstructure.py --market TOKEN_ID --liquidity

# Price impact
python market-microstructure.py --market TOKEN_ID --impact 5000

# Flow analysis
python market-microstructure.py --market TOKEN_ID --flow

# Real-time monitoring
python market-microstructure.py --market TOKEN_ID --monitor 30

# JSON output (for scripts)
python market-microstructure.py --market TOKEN_ID --json
```

## 📊 Key Metrics Interpretation

### Spread (bps)
- **<25** → Excellent, tight market
- **25-50** → Good, reasonable cost
- **50-100** → Fair, watch slippage
- **>100** → Poor, expensive to trade

### Liquidity Score (0-100)
- **80+** → Excellent, trade freely
- **60-79** → Good, normal trading
- **40-59** → Fair, use limit orders
- **<40** → Poor, avoid or tiny size

### Net Pressure
- **>+20%** → Strong BUY pressure (bullish)
- **-20% to +20%** → Balanced
- **<-20%** → Strong SELL pressure (bearish)

### Smart Money Score (0-100)
- **>70** → Sophisticated whales, follow them
- **50-70** → Mixed positioning
- **<50** → Less informed money

### Slippage (for your order size)
- **<0.5%** → Excellent execution
- **0.5-1.0%** → Acceptable
- **1.0-2.0%** → High, consider splitting
- **>2.0%** → Very high, split or wait

## 🎯 Trading Decision Matrix

| Liquidity | Spread | Imbalance | Action |
|-----------|--------|-----------|--------|
| >70 | <50 bps | BUY_PRESSURE | ✅ **LONG** |
| >70 | <50 bps | SELL_PRESSURE | ✅ **SHORT** |
| >70 | <50 bps | BALANCED | ⏸️ Wait |
| 40-70 | 50-100 bps | Any | 🟡 Limit orders only |
| <40 | >100 bps | Any | ❌ **AVOID** |

## 💡 Quick Trading Rules

### ✅ DO:
- Check liquidity before EVERY trade
- Split orders if impact >1%
- Follow whales if Smart Money >70
- Use limit orders when spread >50 bps
- Monitor flow for entry/exit timing

### ❌ DON'T:
- Trade if liquidity score <40
- Market orders in wide spreads
- Orders >10% of total liquidity
- Ignore slippage warnings
- Trade without checking whales

## 🔥 Power User Shortcuts

### Monitor Multiple Markets
```bash
# Create watchlist.txt with token IDs (one per line)
while read market; do
  python market-microstructure.py --market $market --json | \
    jq '{market: .market_id, liq: .liquidity.score, signal: .imbalance.signal}'
done < watchlist.txt
```

### Alert on Whale Activity
```bash
python market-microstructure.py --market TOKEN_ID --whales --json | \
  jq -e '.unusual_volume == true' && \
  echo "🚨 WHALE ALERT!"
```

### Find Best Trading Time
```bash
# Run monitor for a few hours, then analyze
python market-microstructure.py --market TOKEN_ID --monitor 60 --json >> data.jsonl
cat data.jsonl | jq -s 'min_by(.spread.spread_bps) | .timestamp'
```

### Calculate Position Size
```python
from market_microstructure import MarketAnalyzer

analyzer = MarketAnalyzer(token_id)
impact = analyzer.estimate_impact(account_size * 0.02)

position = min(
    account_size * 0.02,      # 2% risk
    impact.optimal_size,       # <1% slippage
    liquidity.total * 0.1      # <10% of market
)
```

## 📈 Metric Formulas

### Spread (bps)
```
spread_bps = ((ask - bid) / mid_price) * 10000
```

### Imbalance Ratio
```
ratio = bid_value / ask_value
net_pressure = (bid - ask) / (bid + ask)
```

### Liquidity Score
```
score = (spread_score * 0.3) + 
        (depth_score * 0.3) + 
        (concentration_score * 0.2) + 
        (resilience_score * 0.2)
```

### Price Impact
```
Walk the order book, sum (price * size)
slippage = (avg_fill_price - reference_price) / reference_price
```

## 🎓 Trading Strategies Cheat Sheet

### Scalping (High Frequency)
```bash
# Requirements
Liquidity: >70
Spread: <30 bps
Refresh: Every 5-10s

# Command
python market-microstructure.py --market TOKEN_ID --monitor 5
```

### Momentum (Swing)
```bash
# Requirements
Net Pressure: >+20% or <-20%
Flow: BULLISH or BEARISH
Liquidity: >60

# Command
python market-microstructure.py --market TOKEN_ID --flow
```

### Large Orders
```bash
# Requirements
Check impact first
Split if slippage >1%
Execute slowly

# Command
python market-microstructure.py --market TOKEN_ID --impact 10000
```

### Market Making
```python
# Requirements
Liquidity: >60
Spread: Stable
Position: <5% of market

# Code
analyzer = MarketAnalyzer(token_id)
spread = analyzer.get_spread()

place_bid(mid * 0.998, size)  # -20 bps
place_ask(mid * 1.002, size)  # +20 bps
```

## 🐋 Whale Tracking Guide

### What to Look For

**Bullish Whales:**
- Large BIDs near current price
- Smart Money Score >70
- Multiple whale bids stacked

**Bearish Whales:**
- Large ASKs near current price
- Defensive positioning
- Whale ASKs at resistance

**Neutral/Inactive:**
- Whales far from mid price
- Balanced bid/ask whales
- Low Smart Money Score

### Interpretation

```
Top whale at $0.52 BID, current price $0.525
→ Whale providing support, bullish signal

Top whale at $0.53 ASK, current price $0.525
→ Whale capping upside, bearish signal

Whales at $0.50 BID / $0.55 ASK
→ Too far to matter, ignore
```

## ⚡ Performance Tips

### API Rate Limits
- Don't spam requests (<1 req/sec)
- Use --monitor mode (refreshes every N seconds)
- Cache results for 10-30s in your bot

### Monitoring Efficiency
```bash
# Efficient: Check every 30s
python market-microstructure.py --market ID --monitor 30

# Inefficient: Manual loop
while true; do
  python market-microstructure.py --market ID
  sleep 1
done  # Too many cold starts!
```

### Data Storage
```python
# Stream to JSONL for later analysis
import json

while True:
    analysis = analyzer.full_analysis()
    
    # Append to file (not overwrite)
    with open('data.jsonl', 'a') as f:
        f.write(json.dumps(analysis) + '\n')
```

## 🔧 Integration Patterns

### Discord Bot
```python
import discord
from market_microstructure import MarketAnalyzer

@bot.command()
async def analyze(ctx, token_id):
    analyzer = MarketAnalyzer(token_id)
    analysis = analyzer.full_analysis()
    
    liquidity = analysis['liquidity']
    signal = analysis['imbalance']['signal']
    
    await ctx.send(f"📊 Liq: {liquidity['score']:.0f} | Signal: {signal}")
```

### Telegram Alerts
```python
import telegram
from market_microstructure import MarketAnalyzer

def check_market(token_id):
    analyzer = MarketAnalyzer(token_id)
    whales = analyzer.detect_whales()
    
    if whales.unusual_volume:
        bot.send_message(chat_id, "🐋 Whale alert!")
```

### Trading Bot
```python
from market_microstructure import MarketAnalyzer

class SimpleBot:
    def run(self):
        analyzer = MarketAnalyzer(self.token_id)
        
        while True:
            imbalance = analyzer.get_imbalance()
            liquidity = analyzer.get_liquidity_metrics()
            
            if liquidity.score > 60:
                if imbalance.signal == "BUY_PRESSURE":
                    self.go_long()
                elif imbalance.signal == "SELL_PRESSURE":
                    self.go_short()
            
            time.sleep(30)
```

## 📱 Mobile-Friendly Commands

### One-Liners for Quick Checks

```bash
# Just the signal
python market-microstructure.py --market ID --json | jq -r '.imbalance.signal'

# Just liquidity score
python market-microstructure.py --market ID --json | jq -r '.liquidity.score'

# Whale count
python market-microstructure.py --market ID --whales --json | jq '.large_positions | length'

# Best spread
python market-microstructure.py --market ID --json | jq -r '.spread.spread_bps'

# Price impact for $1K
python market-microstructure.py --market ID --json | jq -r '.price_impact_1k.slippage_pct'
```

## 🎯 Common Use Cases

### Before Entering Trade
```bash
# Check: Liquidity + Spread + Imbalance
python market-microstructure.py --market TOKEN_ID

# If Liq >60, Spread <100, go ahead
# If Imbalance strong, align with it
```

### Before Large Order
```bash
# Estimate impact
python market-microstructure.py --market TOKEN_ID --impact 10000

# If slippage >1%, split order
```

### Checking Market Quality
```bash
# Quick liquidity check
python market-microstructure.py --market TOKEN_ID --liquidity

# Score <40 → skip this market
```

### Following Smart Money
```bash
# Watch the whales
python market-microstructure.py --market TOKEN_ID --whales

# If Smart Money >70 and whales bullish → go long
```

## 📞 Emergency Troubleshooting

**No data returned:**
```bash
# Check if token ID is correct
curl "https://clob.polymarket.com/book?token_id=YOUR_ID"

# Should return JSON with bids/asks
```

**High slippage warning:**
```
That's real! Don't ignore it.
→ Split your order or wait for better liquidity
```

**Unusual volume alert:**
```
🐋 Whale activity detected!
→ Check --whales for details
→ Consider following their position
```

**Liquidity score dropped:**
```
Market is thinning out.
→ Reduce position size
→ Use limit orders
→ Consider exiting
```

## 💾 Save This File!

```bash
# Keep it handy
cat QUICKREF-microstructure.md

# Or print specific section
sed -n '/## Trading Decision Matrix/,/## 💡 Quick/p' QUICKREF-microstructure.md
```

---

**Print this. Keep it on your desk. Trade smart. 🎯**
