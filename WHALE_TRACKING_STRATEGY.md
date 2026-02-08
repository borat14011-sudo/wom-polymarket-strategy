# Polymarket Whale Wallet Tracking Strategy

## Executive Summary

Polymarket operates on Polygon blockchain with fully transparent on-chain trading data. This document outlines a strategy to identify, track, and potentially copy trade whale wallets on the platform.

**Feasibility: HIGH** - Public leaderboards, transparent blockchain data, and multiple data sources make whale tracking fully viable.

---

## 1. Finding Whale Addresses

### ✅ Public Leaderboard (Primary Source)

Polymarket has a **public leaderboard** at: https://polymarket.com/leaderboard

**Current Top 10 Most Profitable Traders (Monthly):**

| Rank | Username | Wallet Address | Profit (Monthly) | Volume |
|------|----------|----------------|------------------|---------|
| 1 | 0x4924...3782 | `0x492442eab586f242b53bda933fd5de859c8a3782` | +$2,636,064 | $14,237,769 |
| 2 | FeatherLeather | `0xd25c72ac0928385610611c8148803dc717334d20` | +$1,823,591 | $3,388,584 |
| 3 | weflyhigh | `0x03e8a544e97eeff5753bc1e90d46e5ef22af1697` | +$1,067,632 | $6,292,364 |
| 4 | anoin123 | `0x96489abcb9f583d6835c8ef95ffc923d05a86825` | +$901,454 | $6,232,563 |
| 5 | beachboy4 | `0xc2e7800b5af46e6093872b177b7a5e7f0563be51` | +$815,711 | $3,136,903 |
| 6 | tbs8t | `0x4bd74aef0ee5f1ec0718890f55c15f047e28373e` | +$731,911 | $6,174,595 |
| 7 | Countryside | `0xbddf61af533ff524d27154e589d2d7a81510c684` | +$719,023 | $6,467,432 |
| 8 | MrSparklySimpsons | `0xd0b4c4c020abdc88ad9a884f999f3d8cff8ffed6` | +$684,228 | $4,638,506 |
| 9 | BWArmageddon | `0x9976874011b081e1e408444c579f48aa5b5967da` | +$667,568 | $9,421,627 |
| 10 | kch123 | `0x6a72f61820b26b1fe4d956e17b6dc2a1ea3033ee` | +$526,969 | $3,586,545 |

**Leaderboard Features:**
- Filterable by timeframe: Today, Weekly, Monthly, All-Time
- Sortable by Profit/Loss or Volume
- Category filters available
- Searchable by username
- **Direct links to profile pages** with wallet addresses

### 🔍 Additional Data Sources

#### Blockchain Analytics Platforms

1. **Dune Analytics**
   - Public dashboards tracking Polymarket activity
   - SQL queries available for custom analysis
   - Key dashboards:
     - [@datadashboards Polymarket Overview](https://dune.com/datadashboards/polymarket-overview)
     - [@hildobby Volume, OI, Markets dashboard](https://dune.com/hildobby/polymarket)
     - [@alexmccullaaa Historical Accuracy](https://dune.com/alexmccullough/how-accurate-is-polymarket)

2. **Goldsky**
   - Real-time streaming pipelines for Polymarket on-chain activity
   - CryptoHouse integration (SQL queries via ClickHouse)
   - Tracks trades, balances, positions, redeems

3. **Allium**
   - Blockchain analytics platform with Polymarket data
   - Historical trade data queryable via SQL

#### Polymarket APIs

1. **Data API** (`https://data-api.polymarket.com`)
   - Get user positions: `/positions/{proxyWallet}`
   - Returns: size, avgPrice, currentValue, PnL data
   - **No authentication required**

2. **Gamma API** (`https://gamma-api.polymarket.com`)
   - Market discovery and metadata
   - Events, markets, categories, resolution data

3. **CLOB API** (`https://clob.polymarket.com`)
   - Real-time prices and orderbook depth
   - Historical trade data

4. **Subgraph (GraphQL)**
   - Open-source: https://github.com/Polymarket/polymarket-subgraph
   - Volume, user position, market and liquidity data
   - Multiple subgraphs available:
     - activity-subgraph
     - pnl-subgraph (Profit & Loss)
     - orderbook-subgraph

---

## 2. Setting Up Real-Time Alerts

### Option A: WebSocket Monitoring (Recommended)

**Polymarket WebSocket:** `wss://ws-subscriptions-clob.polymarket.com`

**Capabilities:**
- Subscribe to specific user wallet activity
- Monitor orderbook changes in real-time
- Get order status updates
- Track market prices

**Implementation:**
```javascript
// Monitor specific wallet trades
subscribe({
  channel: "user",
  auth: {...},
  markets: ["all"]
});

// Monitor market orderbook
subscribe({
  channel: "market",
  market: "0x..."
});
```

### Option B: Blockchain Event Monitoring

**Polygon RPC Monitoring:**
- Watch for events on Conditional Token Framework (CTF) contracts
- Filter by whale wallet addresses
- Key contracts:
  - CTF Exchange: https://github.com/Polymarket/ctf-exchange
  - Neg-Risk Adapter: https://github.com/Polymarket/neg-risk-ctf-adapter

**Services:**
- Alchemy Notify
- QuickNode Functions
- Custom RPC polling

### Option C: Data API Polling

Poll Data API every 30-60 seconds:
```bash
# Check whale positions
curl https://data-api.polymarket.com/positions/0x492442eab586f242b53bda933fd5de859c8a3782

# Compare against previous snapshot
# Alert on new positions or size changes
```

---

## 3. Automated Copy Trading Strategy

### Trade Execution Pipeline

**Step 1: Detection (< 30 seconds)**
- WebSocket receives whale order notification
- Extract: market, side (BUY/YES or SELL/NO), size, price

**Step 2: Analysis (< 15 seconds)**
- Verify market liquidity (avoid low-volume markets)
- Check current orderbook depth
- Calculate position size (% of whale trade or fixed amount)

**Step 3: Execution (< 45 seconds)**
- Place order via CLOB API
- Use market order for speed or limit order near current price
- Total latency target: **< 90 seconds** (well within 1-5 min window)

### Implementation Tools

**TypeScript SDK:**
```bash
npm install @polymarket/clob-client
```

**Example:**
```typescript
import { ClobClient, Side, OrderType } from "@polymarket/clob-client";

const clobClient = new ClobClient(
  "https://clob.polymarket.com",
  137, // Polygon chain ID
  signer,
  apiCreds
);

// Place order
await clobClient.createAndPostOrder({
  tokenID: "...",
  price: 0.65,
  side: Side.BUY,
  size: 100
}, {
  tickSize: "0.001",
  negRisk: false
}, OrderType.GTC);
```

### Position Sizing Strategy

**Conservative Approach:**
- Copy 1-5% of whale's position size
- Cap max position at $1,000-$5,000 per trade
- Diversify across multiple whales

**Aggressive Approach:**
- Copy 10-20% of whale's position size
- Focus on top 3 whales only
- Higher risk, higher potential reward

---

## 4. Backtesting Capabilities

### ✅ Historical Data Available

**Sources:**
1. **Blockchain Data (Complete History)**
   - All trades recorded on Polygon
   - Query via Dune Analytics, Goldsky, Allium
   - Example Dune query for whale trades:
   ```sql
   SELECT block_time, trader, market, outcome, amount, price
   FROM polymarket.trades
   WHERE trader IN (
     '0x492442eab586f242b53bda933fd5de859c8a3782',
     '0xd25c72ac0928385610611c8148803dc717334d20'
   )
   ORDER BY block_time ASC
   ```

2. **Subgraph Historical Queries**
   - GraphQL interface for historical positions
   - PnL over time
   - Trade history per wallet

3. **Profile Page Data**
   - Each whale profile shows trade history
   - Example: https://polymarket.com/profile/0x492442eab586f242b53bda933fd5de859c8a3782

### Backtesting Methodology

**Step 1: Data Collection**
- Pull all trades from top 10 whales for past 3-6 months
- Include: timestamp, market, outcome, entry price, size, exit price

**Step 2: Simulate Copy Trading**
```python
for whale_trade in whale_trades:
    # Simulate entry with 90-second delay
    our_entry_time = whale_trade.timestamp + 90_seconds
    our_entry_price = get_market_price(whale_trade.market, our_entry_time)
    
    # Simulate exit (copy whale's exit or hold to resolution)
    if whale_trade.has_exit():
        our_exit_price = get_market_price(whale_trade.market, whale_trade.exit_time + 90)
    else:
        our_exit_price = market_resolution_price
    
    pnl = (our_exit_price - our_entry_price) * position_size
```

**Step 3: Performance Metrics**
- Win rate
- Average profit per trade
- Sharpe ratio
- Max drawdown
- Comparison to buy-and-hold of whale portfolio

**Expected Challenges:**
- **Slippage:** Prices may move between whale trade and copy trade
- **Liquidity:** Large whale trades may drain orderbook
- **Market Impact:** Our trades may further move prices
- **Exit timing:** Whales may close positions at different times

---

## 5. Legal & Ethical Framework

### ✅ Legal Considerations

**Public Information:**
- All blockchain data is **public and permissionless**
- Wallet addresses on leaderboard are **voluntarily disclosed**
- No hacking, unauthorized access, or data breach involved
- Similar to watching institutional 13F filings or insider trading disclosures

**Regulatory Status:**
- Polymarket operates as a CFTC-regulated Designated Contract Market (US)
- International platform operates independently
- Copy trading is **not explicitly prohibited** in terms of service
- No front-running (we copy after, not before)

**Comparison to Traditional Markets:**
- Similar to "coattail investing" (copying hedge fund positions)
- Analogous to social trading platforms (eToro, ZuluTrade)
- Following public influencer trades

**Risks:**
- Terms of Service should be reviewed for automation clauses
- Rate limits on API usage
- Potential for account restrictions if deemed abusive

### ⚠️ Ethical Considerations

**Arguments FOR:**
- Information is public and legally accessible
- Whales chose to use public leaderboard
- Similar to learning from successful investors
- Market efficiency: skilled traders get copied, improving price discovery

**Arguments AGAINST:**
- "Parasitic" behavior - profiting from others' research
- Could reduce whale profits if widespread
- May encourage whales to hide activity (use multiple wallets)
- Potential market manipulation if many copy traders cause cascades

**Best Practices:**
- Don't front-run (only copy after whale trades)
- Keep position sizes small relative to market volume
- Contribute your own analysis, don't purely copy
- Consider: Would this strategy work if everyone did it? (Probably not - diminishing returns)

### 🤝 Recommended Ethical Approach

**"Informed Following" vs. "Blind Copying":**
1. Use whale trades as **signals**, not absolute instructions
2. Verify the whale's thesis makes sense
3. Check market fundamentals before copying
4. Maintain your own risk management
5. Diversify across multiple strategies, not just whale-copying

**Transparency:**
- If building this as a commercial product/service, disclose methodology
- Don't misrepresent as your own "alpha"

---

## 6. Implementation Roadmap

### Phase 1: Data Collection (Week 1-2)
- [ ] Scrape leaderboard for top 50 whale addresses
- [ ] Set up Dune Analytics account and queries
- [ ] Extract 6 months of historical trade data
- [ ] Build whale profile database

### Phase 2: Backtesting (Week 3-4)
- [ ] Implement backtesting framework
- [ ] Test various copy trading strategies:
  - Copy top 3 whales
  - Copy top 10 whales
  - Weighted by recent performance
  - Category-specific whales (sports vs. politics)
- [ ] Calculate expected ROI and risk metrics
- [ ] Identify optimal parameters (delay, position size, filters)

### Phase 3: Monitoring System (Week 5-6)
- [ ] Set up WebSocket listener for whale addresses
- [ ] Build alert system (Telegram/Discord bot)
- [ ] Create dashboard showing:
  - Whale positions
  - Recent trades
  - Performance tracking
- [ ] Implement logging and error handling

### Phase 4: Automated Trading (Week 7-8)
- [ ] Integrate CLOB Client SDK
- [ ] Implement order placement logic
- [ ] Add safety checks:
  - Max position size limits
  - Daily loss limits
  - Liquidity checks
- [ ] Paper trade for 1-2 weeks to verify system

### Phase 5: Live Trading (Week 9+)
- [ ] Start with small position sizes ($100-500)
- [ ] Monitor performance daily
- [ ] Iterate based on results
- [ ] Scale up gradually if profitable

---

## 7. Risk Factors & Mitigations

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| API downtime | Missed trades | Multiple data sources, fallback APIs |
| WebSocket disconnection | Delayed detection | Auto-reconnect, heartbeat monitoring |
| Execution latency | Poor fill prices | Optimize code, use market orders when necessary |
| Rate limiting | Blocked API access | Respect rate limits, use multiple API keys |

### Market Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Whale mistakes | Copy losing trades | Diversify across multiple whales |
| Whale manipulation | Intentional bad trades | Filter for consistent performers only |
| Low liquidity | Can't fill orders | Check orderbook depth before trading |
| Adverse selection | Whales exit before us | Set stop-losses, monitor continuously |

### Financial Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Market risk | Lose capital | Position sizing, stop-losses |
| Slippage | Lower profits | Limit order types, avoid thin markets |
| Fees | Erode returns | Calculate fees into expected ROI |

---

## 8. Key Success Metrics

**Performance Tracking:**
- Total P&L (absolute and %)
- Win rate per whale
- Average time in position
- Sharpe ratio
- Maximum drawdown

**Operational Metrics:**
- Detection latency (target: <30s)
- Execution latency (target: <90s)
- API uptime %
- Slippage per trade

**Comparison Benchmarks:**
- Direct copying vs. whale performance
- Copy trading vs. buy-and-hold strategy
- Strategy vs. market average returns

---

## 9. Conclusion

**Feasibility: ✅ HIGHLY VIABLE**

Polymarket's transparent blockchain infrastructure and public leaderboards make whale tracking not only possible but relatively straightforward. The combination of:
- Public wallet addresses
- Real-time APIs and WebSockets
- Complete historical data for backtesting
- Programmatic trading via CLOB SDK

...provides everything needed to implement an automated whale-following strategy.

**Expected Challenges:**
1. **Diminishing Returns:** As more people copy whales, strategy becomes less effective
2. **Execution Lag:** 1-5 minute delay means price slippage risk
3. **Whale Adaptation:** Successful whales may split across wallets to hide activity
4. **Market Impact:** Large copy trades could move prices against us

**Recommended Next Steps:**
1. ✅ Complete backtesting to validate profitability hypothesis
2. ⚠️ Start with paper trading to test infrastructure
3. 💰 Begin live trading with small capital ($1K-5K)
4. 📊 Track and iterate based on real performance

**Legal/Ethical Verdict:**
This strategy operates in a **legal gray area** but leans toward **acceptable**:
- Uses only public information
- No unauthorized access
- Similar to established practices in traditional finance
- However, purely extractive with no value-add to the ecosystem

**Recommendation:** Proceed with **informed following** approach rather than blind copying. Use whale trades as one signal among many in a broader trading strategy.

---

## Appendix A: Useful Resources

**Documentation:**
- Polymarket Docs: https://docs.polymarket.com
- CLOB Client GitHub: https://github.com/Polymarket/clob-client
- Subgraph GitHub: https://github.com/Polymarket/polymarket-subgraph

**Data Sources:**
- Leaderboard: https://polymarket.com/leaderboard
- Dune Analytics: https://dune.com/polymarket
- Goldsky Docs: https://docs.goldsky.com/chains/polymarket

**APIs:**
- Gamma API: https://gamma-api.polymarket.com
- CLOB API: https://clob.polymarket.com
- Data API: https://data-api.polymarket.com
- WebSocket: wss://ws-subscriptions-clob.polymarket.com

**Community:**
- Discord: https://discord.gg/polymarket
- Twitter: https://x.com/polymarket
- Help Center: https://help.polymarket.com

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Status:** Research Complete - Ready for Backtesting Phase
