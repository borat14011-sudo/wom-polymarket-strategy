# 🐋 Polymarket Whale & Bot Tracking System

> **Autonomous smart money tracking for Polymarket prediction markets**

---

## 📁 System Overview

This tracking system monitors Polymarket for:
- **Whale activity** (>$50K positions)
- **Bot patterns** (automated trading strategies)
- **Capital flows** (smart money movements)

---

## 📊 Output Files

| File | Description | Update Frequency |
|------|-------------|------------------|
| `WHALE_ALERTS.md` | Smart money signals and whale wallet tracking | Every hour |
| `BOT_MIRRORING.md` | Detected bot strategies to copy | Every hour |
| `FLOW_ANALYSIS.md` | Capital movement and flow analysis | Every hour |

---

## 🚀 Quick Start

### Manual Update
```bash
node polymarket-tracker.js
```

### Automated Updates (Windows)
```powershell
# Run every hour
schtasks /create /tn "PolymarketTracker" /tr "node C:\path\to\polymarket-tracker.js" /sc hourly
```

### Automated Updates (Linux/Mac)
```bash
# Add to crontab (runs every hour)
0 * * * * cd /path/to/workspace && node polymarket-tracker.js
```

---

## 🎯 Trading Applications

### 1. Follow Whale Entries/Exits
- Monitor `WHALE_ALERTS.md` for large position changes
- Enter when whales accumulate
- Exit when whales distribute

### 2. Copy Bot Strategies
- Use `BOT_MIRRORING.md` for strategy templates
- Mirror arbitrage and market-making bots
- Requires fast execution

### 3. Front-Run Institutional Moves
- Track flow analysis for early signals
- Enter before price moves
- Requires quick reaction time

### 4. Avoid Whale Stop-Hunts
- Identify whale support/resistance levels
- Don't place stops where whales hunt
- Use wider stops in whale-heavy markets

---

## 📈 API Data Sources

| Source | Endpoint | Data |
|--------|----------|------|
| Gamma API | `/markets` | Market metadata, volume, liquidity |
| CLOB API | `/markets` | Order book data, pricing |
| Activity Feed | Web scraping | Real-time trades |

---

## 🐋 Whale Detection Criteria

| Tier | Threshold | Signal |
|------|-----------|--------|
| Mega Whale | >$50M volume | 🔴 |
| Whale | >$10M volume | 🟢 |
| Dolphin | >$1M volume | 🟡 |
| Shark | >$100K 24h flow | 🔵 |

---

## 🤖 Bot Detection Criteria

| Type | Signature | Confidence |
|------|-----------|------------|
| Arbitrage | 15-min interval trades | 95% |
| Market Maker | Tight spread maintenance | 90% |
| Trend Follower | Momentum entries | 75% |
| Mean Reversion | Counter-trend orders | 70% |

---

## ⚠️ Risk Disclaimer

> **IMPORTANT:** This system provides analysis, not financial advice.
> 
> - Past whale/bot activity doesn't guarantee future performance
> - Markets can turn against smart money
> - Never risk more than you can afford to lose
> - Always do your own research

---

## 🔧 Configuration

Edit `polymarket-tracker.js` to customize:

```javascript
const CONFIG = {
    whaleThreshold: 50000,      // Whale classification threshold
    largeOrderThreshold: 10000,  // Large order threshold
    botTradeSize: 50,           // Bot detection trade size
    updateInterval: 3600000,    // Update interval (ms)
    marketsToTrack: 100,        // Markets to analyze
};
```

---

## 📚 Documentation

- [WHALE_ALERTS.md](WHALE_ALERTS.md) - Live whale tracking
- [BOT_MIRRORING.md](BOT_MIRRORING.md) - Bot strategy replication
- [FLOW_ANALYSIS.md](FLOW_ANALYSIS.md) - Capital flow analysis

---

## 🔄 Update Schedule

- **Market Hours:** Every hour (00:00, 01:00, etc.)
- **Off Hours:** Every 4 hours
- **High Volatility:** Every 15 minutes (manual trigger)

---

## 🛠️ Troubleshooting

### API Errors
- Check internet connection
- Verify API endpoints are accessible
- Check for rate limiting

### No Data Updates
- Ensure `polymarket-tracker.js` has execute permissions
- Check file write permissions
- Verify Node.js version (v16+)

### Incorrect Analysis
- Markets may be closed or illiquid
- API data may be delayed
- Consider manual verification

---

## 📝 Changelog

### v1.0.0 (2026-02-09)
- Initial release
- Whale tracking system
- Bot detection algorithms
- Flow analysis engine
- Automated report generation

---

**System Status:** ✅ OPERATIONAL  
**Last System Update:** 2026-02-09 03:51 UTC

---

*Built for tracking smart money on the world's largest prediction market.*
