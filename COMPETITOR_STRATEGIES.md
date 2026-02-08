# COMPETITOR STRATEGIES - Polymarket Professional Traders Research

**Research Date:** February 6, 2026  
**Focus:** Real-world profitable strategies, bots, and traders (not theory)

---

## 🎯 EXECUTIVE SUMMARY

Professional Polymarket traders are making money through:
1. **Copy Trading Bots** - Following profitable wallets automatically
2. **Arbitrage Strategies** - Exploiting price inefficiencies (UP + DOWN < $1.00)
3. **Limit Order Pre-placement** - Getting in early on 1-hour markets at $0.45
4. **15-Min BTC Markets** - High-frequency arbitrage on crypto updown markets
5. **Market Making** - Providing liquidity and earning spreads

**Key Insight:** Most profitable traders use BOTS, not manual trading. Speed = edge.

---

## 📈 PROFITABLE STRATEGIES (REAL-WORLD)

### 1. Copy Trading (Most Popular)
**What it is:** Automatically replicate trades from successful wallets  
**How it works:**
- Monitor top trader wallets via blockchain/API
- Detect when they place orders
- Copy their trades with proportional sizing
- Diversify across 3-5 profitable traders

**Actual Implementation:**
- **earthskyorg/Polymarket-Copy-Trading-Bot** (526 stars, TypeScript/Rust/Python)
  - Monitors Polymarket Data API every 1 second
  - Smart position sizing based on capital ratios
  - Tiered multipliers for risk management
  - MongoDB tracking of all trades
  - Contact: [@opensea712](https://t.me/opensea712) on Telegram

- **soulcrancerdev/polymarket-trading-bots** (332 stars, Rust)
  - Production copy trading bot with Telegram UI
  - Multiple copy strategies: PERCENTAGE, FIXED, ADAPTIVE
  - Multi-trader support
  - Contact: [@soulcrancerdev](https://t.me/soulcrancerdev)
  - Demo bot: https://t.me/poly_copy_tg_bot

**Who to copy:**
- Use **PredictFolio.com** to analyze trader history
- Look for: Positive P&L curve, >55% win rate, consistent activity
- Top traders listed on https://polymarket.com/leaderboard
- Popular tracked: Dropper, 25usdc, GayPride, aenews2, ImJustKen, Car

**Risk Management:**
- Limit risk to 7% per trade, max 3 open positions
- Start with 0.1% allocation for testing
- Copy 50-100% of trader's size
- Cap max trade size (e.g., $50-100)
- Filter by market type (e.g., only copy 1-hour markets)

---

### 2. Arbitrage Strategies

#### A. Simultaneous Balanced Orders
**Core principle:** When UP_price + DOWN_price < $1.00, buy both sides  
**Example:**
- UP = $0.74, DOWN = $0.25
- Total = $0.99 < $1.00
- Profit: $0.01 per contract (1% return)
- One side ALWAYS pays $1.00 at resolution

**Challenge:** Liquidity changes every second, hard to fill both legs simultaneously

**Implementation:**
- **ddev05/polymarket-trading-bot** (353 stars, Python)
  - Monitors BTC/ETH 15m & 1h markets
  - WebSocket real-time price updates
  - Calculates optimal bet sizes: k = total_bet / (UP_price + DOWN_price)
  - Contact: [@DDev05](https://t.me/ddev05)

#### B. 15-Minute BTC Arbitrage
**Specific strategy:** BTC up/down 15-minute markets  
**Implementation:**
- **gabagool222/15min-btc-polymarket-trading-bot** (161 stars, Python)
  - Pure arbitrage: buy both when total < $0.991
  - Continuous scanning with no delays
  - Paired execution verification (cancels if only one leg fills)
  - Auto-switches to next market when current closes
  - Uses FOK (Fill-Or-Kill) orders to avoid partial fills
  - Contact: [@gabagool222](https://t.me/gabagool222)

**Key settings:**
- TARGET_PAIR_COST: 0.991 (max combined price)
- ORDER_SIZE: Start with 5 shares minimum
- ORDER_TYPE: FOK (recommended)
- COOLDOWN_SECONDS: 10 (between executions)

#### C. Price Impact Arbitrage
**Advanced strategy:** Buy large quantity of one side to move price, then buy opposite  
**When:** UP_price + DOWN_price is close to $1.00 but not quite arb  
**Requires:** Sufficient liquidity calculation, precise timing

---

### 3. Limit Order Strategy (1-Hour Markets) ⭐ RECOMMENDED

**Why 1-hour > 15-minute:**
- 15m markets often move in one direction only
- 1h markets have multiple price cycles
- Higher probability of limit orders matching
- More stable, lower risk

**The Strategy:**
1. **Market Initialization:** When new 1-hour market opens, immediately place:
   - UP limit order: $0.45
   - DOWN limit order: $0.45
   - Total cost if both fill: $0.90
   - Guaranteed profit: $0.10 (10% return)

2. **Order Matching:** Over 1 hour, prices fluctuate and orders match at different times

3. **Profit Realization:** One side pays $1.00, you paid $0.90

**Why it works:**
- Continuous liquidity changes over longer period
- Price movements are more balanced
- Market dynamics create natural oscillations
- Works on "next live markets" - place orders early

**Implementation notes:**
- Focus on crypto markets (BTC, ETH, SOL, XRP) - highest activity
- Place orders immediately when market initializes
- Use limit orders to prevent overpaying

---

### 4. Market Making (Coming Soon)
**Concept:** Provide liquidity on both sides, earn the spread  
**Status:** Several bots developing this (Strategy 5 in various repos)  
**Features planned:**
- Continuous bid/ask orders on both sides
- Dynamic spread management based on conditions
- Inventory balancing to minimize risk
- Profit from bid-ask spreads

---

## 🐙 GITHUB TRADING BOTS (RANKED BY STARS)

| Repository | Stars | Language | Strategy | Last Updated |
|------------|-------|----------|----------|--------------|
| earthskyorg/Polymarket-Copy-Trading-Bot | 526 | TypeScript/Rust/Python | Copy trading | 5 days ago |
| Adraylis/polymarket-copy-trading-bot | 820 | TypeScript | Copy trading | 8 hours ago |
| dexorynlabs/polymarket-trading-bot-python | 438 | Python | Copy trading | Yesterday |
| ddev05/polymarket-trading-bot | 353 | Python | Arbitrage | 17 hours ago |
| soulcrancerdev/polymarket-trading-bots | 332 | Rust | Copy/Arb/MM | 8 hours ago |
| thesSmartApe/polymarket-copy-trading-bot-python | 317 | Python | Copy trading | 8 days ago |
| thesSmartApe/polymarket-copy-trading-bot-rust | 228 | Rust | Copy trading | 2 days ago |
| runesatsdev/polymarket-trading-bot | 200 | Python | Copy/Arb | 25 days ago |
| gabagool222/15min-btc-polymarket-trading-bot | 161 | Python | BTC arbitrage | 3 days ago |
| gabagool222/Polymarket-Arbitrage-Trading-Bot | 159 | Rust | Arbitrage | 4 days ago |

**Note:** Many repos are ACTIVELY MAINTAINED (updates within last week)

---

## 👥 TRADER COMMUNITIES & CONTACTS

### Telegram Contacts (Bot Developers)
- **@opensea712** - earthskyorg copy trading bot
- **@soulcrancerdev** - Rust trading bots, Telegram UI
- **@DDev05** - Arbitrage bot developer
- **@gabagool222** - 15min BTC arbitrage specialist

### Trading Communities
- **Polymarket Discord:** discord.com/invite/polymarket (official)
- **Telegram groups:** Multiple private groups run by bot developers
- **Bot UIs:** Some devs offer Telegram bot interfaces for easier setup
  - Demo: https://t.me/poly_copy_tg_bot
  - Production: https://t.me/poly_copy_prod_tg_bot

### Analytics Tools
- **PredictFolio.com** - THE tool for trader analysis
  - Track 1M+ Polymarket users
  - 30,000+ open markets tracked
  - 5 years of historical data
  - Search traders by handle, market, performance
  - Compare P&L, volume, win rate
  - Follow top traders with instant insights
  - Popular tracked: @Dropper, @25usdc, @GayPride, @aenews2

- **Polymarket Leaderboard:** polymarket.com/leaderboard
  - Official rankings
  - Filter by timeframe
  - Wallet addresses visible for copying

---

## 🎯 SIGNALS & STRATEGIES PROFESSIONALS USE

### Copy Trading Selection Criteria
**Portfolio approach:**
- Diversify across 3-5 traders with specific market expertise
- Analyze wallet history: P&L curve, win rate, risk-reward, max drawdown
- Use "Copy Score" = R² × win rate × profit factor
- Avoid loud whales; target small quants with steady profits

**Target trader types:**
1. **AI Sentiment Bots** - Profit from news reactions (5-20 min window)
2. **Mean Reversion Bots** - Snap up panic dumps
3. **Undervaluation Traders** - Low-attention, mispriced markets
4. **Low/High Price Specialists:**
   - Low-entry (0.1¢) high-frequency plays
   - High-entry (99¢) near-resolution plays

**Wallet Baskets Approach:**
- Group 5-10 similar wallets
- Enter only when 80%+ align on same outcome
- Within tight price range

### Market Selection
**Best markets for bots:**
- **BTC/ETH 1-hour markets** - Highest activity, best for limit orders
- **BTC 15-minute** - High-frequency arbitrage
- **Political markets** - If following news-reactive traders
- **Sports (low leagues)** - Often mispriced, undervalued

**Avoid:**
- Low liquidity markets (<$1M volume)
- Single-direction 15m markets (for limit orders)
- Unfamiliar domains (e.g., NHL if you don't know hockey)

### Position Sizing
**Proportional approach:**
- If whale risks 5% of $1M, you risk 5% of your portfolio
- Not dollar-for-dollar copying

**Risk limits:**
- Cap risk at 7% per trade
- Max 3 open positions
- Start small (0.1% allocation) for testing
- Use multipliers for different trade sizes

### Technical Execution
**Order types:**
- **FOK (Fill-Or-Kill):** Recommended for arbitrage to avoid one-leg fills
- **GTC (Good Till Cancel):** For limit orders
- **FAK (Fill-And-Kill):** For copy trading with retries

**Latency optimization:**
- Use VPS near Polygon nodes (sub-1ms)
- TradingVPS.io popular among traders (Amsterdam recommended for geo restrictions)
- WebSocket feeds for real-time data (lower latency than polling)

---

## 🛠️ TECHNICAL IMPLEMENTATION

### Required Infrastructure
1. **Polymarket API Credentials:**
   - Private key from wallet
   - API key/secret/passphrase (generated from private key)
   - Signature type: 0 (EOA), 1 (Magic.link), 2 (Gnosis Safe)
   - Funder address (for proxy wallets)

2. **Blockchain Access:**
   - Polygon RPC endpoint (Infura/Alchemy/QuickNode)
   - USDC balance on Polygon
   - Token allowances (for MetaMask/EOA users)

3. **Database:**
   - MongoDB (most common) for trade history
   - Free tier available on MongoDB Atlas

4. **Monitoring:**
   - Real-time price data (WebSocket or 1-second polling)
   - Market discovery (Gamma API for finding markets)

### Technology Stacks Used
**TypeScript:**
- ethers.js for blockchain
- @polymarket/clob-client (official)
- mongoose for MongoDB
- Docker deployment common

**Python:**
- web3.py for blockchain
- py-clob-client (official)
- pymongo
- asyncio for concurrent ops

**Rust:**
- ethers-rs for blockchain
- tokio async runtime
- mongodb crate
- High performance, sub-millisecond execution

---

## 💰 PROFITABILITY INSIGHTS

### What Works (Based on Bot Implementations)
1. **Copy trading with portfolio diversification** - Most accessible
2. **BTC 15-min arbitrage** - Small but consistent gains (1% per trade)
3. **1-hour limit orders** - 10% ROI when both legs fill
4. **Early market entry** - Place limit orders at $0.45 when markets open

### What Doesn't Work
1. **Manual trading** - Too slow, bots have the edge
2. **Single-trader copying** - High risk if they have bad run
3. **15-min limit orders** - Often single-direction, orders don't match
4. **High-spread markets** - Spreads eliminate arbitrage profit

### Actual Returns (From Documentation)
- **Arbitrage:** 1-10% per successful trade
- **Copy trading:** Dependent on copied trader's performance
- **Limit orders (1h):** 10% when both legs fill at $0.45
- **15-min BTC arb:** $0.01-0.05 profit per opportunity

### Risk Factors
- Liquidity risk - orders may not fill
- Price slippage - market orders fill at worse prices
- Partial fills - one-leg risk (requires FOK orders)
- Market volatility - prices change rapidly
- Execution delays - network latency matters

---

## 🎓 PRE-COPY CHECKLIST (From Professionals)

✅ **Before automating:**
1. Trade manually first (10-20 trades) to understand risk
2. Observe 5-10 trades before automating
3. Match trader expertise to your interests
4. Ensure liquid markets (min $1M volume)
5. Test in DRY_RUN mode thoroughly

✅ **Portfolio construction:**
1. Diversify across 3-5 traders minimum
2. Different market specializations (sports, politics, crypto)
3. Verify track record on PredictFolio
4. Look for >55% win rate, positive P&L curve
5. Check max drawdown tolerance

✅ **Risk management:**
1. Set max trade size (e.g., $50-100)
2. Limit to 7% risk per trade
3. Max 3 concurrent positions
4. Use stop-loss if bot supports
5. Monitor adverse selection (slippage + fees eating profit)

---

## 🔮 EMERGING TRENDS

### Market Maker Bots (Next Wave)
- Multiple repos implementing
- Provide liquidity, earn spreads
- Dynamic spread management
- Inventory balancing

### Advanced Features Appearing
- Machine learning price prediction
- Multi-asset support (beyond BTC/ETH)
- Advanced order types (stop-loss, take-profit)
- Portfolio optimization
- Web dashboards for monitoring
- Mobile notifications

### Telegram UI Integration
- Bot control via Telegram
- Real-time notifications
- Easy configuration
- No coding required for users

---

## 📊 COMPARISON: STRATEGIES

| Strategy | Profit/Trade | Frequency | Complexity | Risk | Best For |
|----------|-------------|-----------|------------|------|----------|
| Copy Trading | Variable | Medium | Low | Medium | Beginners |
| BTC 15m Arb | 1% | High | Medium | Medium | Automation |
| 1h Limit Orders | 10% | Low | Low | Low | Patient traders |
| Arbitrage (general) | 1-5% | Medium | High | Medium-High | Experienced |
| Market Making | 0.5-2% | Very High | Very High | Medium | Advanced |

---

## 🎯 ACTIONABLE RECOMMENDATIONS

### If Starting from Scratch:
1. **Study PredictFolio** - Analyze top traders for 1-2 weeks
2. **Manual test** - Place 10-20 trades yourself to learn
3. **Start with copy trading** - Lowest barrier, proven profitable
4. **Use established bot** - earthskyorg or soulcrancerdev repos
5. **Paper trade first** - DRY_RUN mode until confident

### For Maximum Profit:
1. **1-hour limit order strategy** - Best risk/reward (10% ROI)
2. **Multiple bots** - Run copy + arbitrage simultaneously
3. **VPS hosting** - Low latency = edge (TradingVPS.io)
4. **Diversify across 5 traders** - Reduce single-trader risk
5. **Focus on liquid markets** - BTC, ETH, major political events

### For Lowest Risk:
1. **1-hour limit orders only** - Predictable, bounded risk
2. **Small position sizes** - Start with 5 shares
3. **Strict filters** - Only copy certain market types
4. **FOK orders** - Avoid partial fills
5. **Conservative thresholds** - Higher arbitrage minimums

---

## 📞 KEY CONTACTS FOR FURTHER RESEARCH

### Active Developers (Telegram)
- @opensea712 - Comprehensive copy trading suite
- @soulcrancerdev - Rust bots with UI
- @DDev05 - Arbitrage specialist
- @gabagool222 - BTC 15min expert

### Communities
- Polymarket Discord - discord.com/invite/polymarket
- PredictFolio - Analytics platform
- Various Telegram groups (private, invite-only)

---

## 🔗 RESOURCES

### Official Documentation
- Polymarket CLOB API: https://docs.polymarket.com
- py-clob-client: https://github.com/Polymarket/py-clob-client
- Gamma Markets API: https://docs.polymarket.com/developers/gamma-markets-api/get-markets

### Analytics
- PredictFolio.com - Trader tracking
- Polymarket.com/leaderboard - Official rankings

### Bot Repositories
- See GitHub section above for specific repos
- Most are open-source, actively maintained
- Multiple language implementations available

---

**BOTTOM LINE:** Professional Polymarket traders use BOTS, not manual trading. The edge comes from:
1. **Speed** (automated execution)
2. **Consistency** (no emotion, pure strategy)
3. **Diversification** (multiple traders/strategies)
4. **Analytics** (PredictFolio for trader selection)

The most profitable approach is **copy trading 3-5 proven traders** combined with **1-hour limit order arbitrage**. Both are low-complexity, proven strategies with active bot implementations available.

---

*Research completed: February 6, 2026*  
*Sources: GitHub (400+ repos), PredictFolio, Polymarket official docs, Telegram developer contacts*
