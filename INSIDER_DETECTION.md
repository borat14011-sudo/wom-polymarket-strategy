# Insider Trading Detection on Polymarket

**Research Date:** 2026-02-07  
**Status:** Research Phase  
**Theory:** Sudden price moves before public news may signal insider information

---

## Executive Summary

Prediction markets like Polymarket aggregate information from traders. When prices move significantly before news breaks, it may indicate:
1. **Informed trading** - Someone with inside information placing bets
2. **Smart money** - Sophisticated traders with superior analysis
3. **Coordinated manipulation** - Groups moving prices deliberately
4. **Random noise** - Statistical artifacts or lucky timing

This document explores detection strategies, backtesting methods, and legal/ethical considerations.

---

## Part 1: The Theory

### How Insider Trading Works on Prediction Markets

**Traditional Markets vs Prediction Markets:**
- **Stock Market:** Material non-public information (MNPI) used for trading
- **Polymarket:** Advance knowledge of outcomes (election results, event timing, etc.)

**Key Indicators:**
- Sudden 10%+ price movements with no corresponding news
- Unusually large positions taken by single wallets
- Price moves 1-48 hours before official announcements
- Volume spikes with directional bias

**Why It Matters:**
- Can identify "smart money" early
- May predict news before it breaks
- Reveals information asymmetry in markets

---

## Part 2: Detection Strategy

### Stage 1: Monitor for Anomalous Price Moves

**Criteria for Suspicious Activity:**
```
IF price_change >= 10% in < 1 hour
AND no_public_news_catalyst
AND volume > 2x daily_average
THEN flag_for_investigation
```

**Data to Track:**
- Minute-by-minute price changes
- Order book depth changes
- Individual wallet activity (blockchain transparency)
- Time-to-news correlation

**Tools Needed:**
- Polymarket API for market data
- News aggregator (Twitter, Google News, Bloomberg Terminal)
- Blockchain explorer for wallet tracking
- Statistical analysis for baseline volatility

### Stage 2: News Correlation Analysis

**Methodology:**
1. Identify all 10%+ moves in time window T
2. Search for related news in [T+1h, T+48h]
3. Calculate correlation strength:
   - **Direct correlation:** News directly confirms the price move
   - **Indirect correlation:** Related but not definitive
   - **No correlation:** Price moved, no news emerged

**Scoring System:**
```
Suspicion Score = 
  (price_magnitude × 10) + 
  (volume_ratio × 5) + 
  (time_to_news_hours × -0.5) +
  (wallet_concentration × 15)
```

**Thresholds:**
- Score < 50: Likely noise
- Score 50-80: Potentially informed trading
- Score > 80: High probability insider activity

### Stage 3: Wallet Pattern Analysis

**Smart Money Indicators:**
- Consistent early entries before news (>70% hit rate)
- Large position sizes relative to market depth
- Quick entries followed by steady holding
- Multiple markets showing same pattern

**Tracking Methods:**
- Polymarket runs on Polygon blockchain (transparent)
- Use Polygonscan to track wallet histories
- Build database of "known smart wallets"
- Monitor for clustering (multiple wallets coordinating)

---

## Part 3: Backtesting Framework

### Historical Analysis Approach

**Data Requirements:**
1. **Market data:** All Polymarket trades (2020-present)
2. **News timestamps:** Archive of major announcements
3. **Wallet histories:** On-chain transaction data
4. **Market metadata:** Volume, liquidity, participant counts

**Backtesting Process:**

```python
# Pseudocode for backtesting algorithm

for each market in historical_markets:
    baseline_volatility = calculate_std_dev(prices[-30d])
    
    for each hour in market.lifetime:
        price_change = (current - previous) / previous
        
        if abs(price_change) > 0.10:  # 10% threshold
            # Check for news in next 48 hours
            news_events = search_news(
                topic=market.topic,
                timeframe=(current + 1h, current + 48h)
            )
            
            if news_events:
                # This was a "predictive move"
                record_event(
                    market=market,
                    price_change=price_change,
                    time_to_news=news_events[0].timestamp - current,
                    wallets=get_active_wallets(hour)
                )
```

**Key Metrics to Extract:**
- **Hit rate:** % of 10%+ moves followed by confirming news
- **Time distribution:** How many hours before news do prices move?
- **Magnitude correlation:** Do bigger moves predict bigger news?
- **Wallet persistence:** Do same wallets appear repeatedly?

### Case Study Candidates (Historical Examples)

**Election Markets:**
- Early moves before candidate announcements
- VP pick predictions before official reveals
- Polling data leaks

**Corporate Events:**
- Acquisition announcements
- Earnings surprises
- Executive departures

**Geopolitical Events:**
- Military actions
- Diplomatic agreements
- Regulatory decisions

---

## Part 4: Real-World Examples & Patterns

### Example 1: Hypothetical VP Pick Scenario

**Timeline:**
- **Day 1, 10:00 AM:** Market for "Will candidate X pick Y as VP?" at 35%
- **Day 1, 2:00 PM:** Sudden spike to 52% (17% move, $500K volume)
- **Day 1, 2:00-8:00 PM:** No public news, market stabilizes at 50%
- **Day 2, 9:00 AM:** Official VP announcement confirms candidate Y

**Analysis:**
- 19-hour advance signal
- No news catalyst during initial move
- Possible insider: campaign staff, family, journalists with advance briefing

**Wallet Behavior:**
- Single wallet placed $200K bet in 30 minutes
- Wallet history shows 3 prior similar "early moves" with 100% accuracy

**Suspicion Score:** 92 (HIGH)

### Example 2: Tech Product Launch

**Timeline:**
- Market: "Will Company Z release product before Q2?"
- Sudden 15% YES move 36 hours before press release
- Volume 3x normal
- 5 wallets account for 80% of buying

**Analysis:**
- Could be informed trading (employees, suppliers, press)
- Could also be leaked marketing materials
- Wallets show history of tech market trading (could be sector experts)

**Suspicion Score:** 68 (MODERATE - ambiguous)

### Example 3: False Positive - Noise

**Timeline:**
- Political resignation market moves 12% on no news
- No resignation occurs in next week
- Price reverts to baseline

**Analysis:**
- Likely rumor or misinterpretation
- No actual insider information
- Demonstrates need for news confirmation

---

## Part 5: Legal & Ethical Considerations

### Legal Status

**Current Regulatory Landscape:**

1. **CFTC Jurisdiction:**
   - CFTC regulates event contracts/prediction markets in US
   - Polymarket faced enforcement action in 2022, paid $1.4M fine
   - Now operates with geographic restrictions for US users

2. **Insider Trading Laws:**
   - Traditional insider trading laws (Securities Exchange Act §10b-5) apply to securities
   - **Unclear** if they apply to prediction markets
   - No major enforcement cases yet for prediction market insider trading

3. **Material Non-Public Information (MNPI):**
   - Corporate insiders trading on Polymarket may violate existing laws
   - Example: CEO betting on own company's earnings = likely illegal
   - Political insiders betting on election outcomes = gray area

**Legal Risk Assessment:**

| Activity | Risk Level | Reasoning |
|----------|-----------|-----------|
| Trading on your own insider info | HIGH | Likely violates existing laws |
| Following suspicious wallets | LOW | Public blockchain data, no trading on MNPI yourself |
| Building detection systems | LOW | Research & analysis of public data |
| Alerting regulators to patterns | LOW | Whistleblowing is protected |

### Ethical Considerations

**The "Following Smart Money" Dilemma:**

**Arguments FOR:**
- Blockchain is public; you're analyzing available information
- No different than following institutional trades in stocks
- Helps market efficiency by spreading information faster
- You're not the one trading on insider info

**Arguments AGAINST:**
- Profiting from potentially illegal activity (even indirectly)
- May encourage more insider trading if it becomes profitable to follow
- Undermines market integrity
- Creates two-tiered system (those who can detect vs. cannot)

**Recommendation:**
- **Detection & Research:** Ethically sound, can improve market design
- **Following for Profit:** Gray area, proceed with caution
- **Using Your Own Insider Info:** Clearly unethical and likely illegal
- **Public Reporting:** Consider publishing findings to improve transparency

### Comparison to Traditional Markets

**Stock Market Parallels:**
- **Unusual Options Activity (UOA):** Traders monitor for suspicious options before announcements
- **Dark Pool Tracking:** Institutional order flow analysis
- **13F Filings:** Following "smart money" fund managers legally

**Key Difference:**
- Prediction markets have blockchain transparency
- Much easier to track individual wallets vs. traditional brokerage accounts
- Smaller markets = easier to manipulate

---

## Part 6: Implementation Roadmap

### Phase 1: Data Collection (Weeks 1-2)

**Build Infrastructure:**
- [ ] Set up Polymarket API access
- [ ] Create database for historical market data
- [ ] Implement news scraping (Twitter API, Google News)
- [ ] Build blockchain monitoring for wallet tracking

**Data Schema:**
```sql
markets (id, topic, created_at, resolved_at, volume, outcome)
prices (market_id, timestamp, price, volume)
trades (market_id, wallet, timestamp, size, direction)
news_events (timestamp, topic, source, relevance_score)
wallets (address, total_volume, win_rate, avg_early_entry)
```

### Phase 2: Historical Backtesting (Weeks 3-4)

- [ ] Download all historical Polymarket data
- [ ] Run detection algorithm on past markets
- [ ] Correlate with news archives
- [ ] Identify top 50 "suspicious events"
- [ ] Deep dive on 10 case studies

**Target Metrics:**
- Baseline: What % of 10%+ moves have news within 48h?
- How many hours advance notice on average?
- Which market categories show strongest signals?

### Phase 3: Live Monitoring (Week 5+)

- [ ] Deploy real-time price monitoring
- [ ] Alert system for 10%+ moves
- [ ] Automated news correlation checks
- [ ] Dashboard for visualization

**Alert Template:**
```
🚨 INSIDER SIGNAL DETECTED
Market: [Market Name]
Price Move: X% in Y minutes
Volume: Z (Abn normal: +W%)
Top Wallets: [addresses]
News Check: [None found / Possible correlation]
Suspicion Score: XX/100
```

### Phase 4: Wallet Intelligence (Ongoing)

- [ ] Build "smart wallet" database
- [ ] Track historical performance
- [ ] Identify coordinated wallets
- [ ] Create reputation scoring

---

## Part 7: Limitations & Challenges

### Detection Challenges

1. **False Positives:**
   - Legitimate informed analysis (not insider info)
   - Coordinated public information interpretation
   - Random chance in high-volume markets

2. **Attribution Problem:**
   - Can't prove insider info without confession
   - Correlation ≠ causation
   - May be sophisticated modeling, not insider knowledge

3. **Market Manipulation:**
   - Whale trades can move prices without insider info
   - Spoofing and wash trading harder to detect
   - May be deliberately misleading to cause false signals

4. **Data Limitations:**
   - News timestamp precision (when was info truly "public"?)
   - Wallet mixing and privacy techniques
   - Off-chain coordination (Telegram groups, private signals)

### Technical Limitations

- API rate limits
- Historical data availability
- News archive completeness
- Computational resources for real-time monitoring

---

## Part 8: Conclusions & Recommendations

### Key Findings

1. **Detection is Feasible:**
   - Blockchain transparency enables wallet tracking
   - Price-news correlation can be quantified
   - Pattern analysis can identify suspicious activity

2. **Legal Gray Area:**
   - Following patterns = likely legal
   - Trading on your own insider info = likely illegal
   - No clear precedent for prediction markets specifically

3. **Ethical Considerations:**
   - Research and transparency = good
   - Profit from following insiders = questionable
   - Should be disclosed if monetized

### Practical Strategy

**If Building This System:**

1. **Start with Research:**
   - Backtest thoroughly before any trading
   - Publish findings to contribute to market integrity
   - Consider academic collaboration

2. **Legal Protection:**
   - Consult crypto/fintech attorney
   - Document that you're analyzing public blockchain data
   - Don't trade on material non-public info yourself

3. **Ethical Framework:**
   - Transparency: Publish methodology
   - Education: Help others understand market dynamics
   - Boundaries: Don't cross into market manipulation

**Best Use Cases:**

✅ **GOOD:**
- Academic research on prediction market efficiency
- Building tools for regulators
- Public dashboards showing market anomalies
- Improving market design

⚠️ **GRAY AREA:**
- Following "smart wallets" for personal trading
- Selling insider detection as a service
- Creating alpha from pattern recognition

❌ **BAD:**
- Using your own insider information to trade
- Market manipulation based on detection signals
- Targeting specific individuals for harassment

---

## Part 9: Resources & Tools

### Data Sources

**Polymarket:**
- API: https://docs.polymarket.com/
- Subgraph: GraphQL endpoint for historical data
- Website markets: https://polymarket.com/

**Blockchain:**
- Polygonscan: https://polygonscan.com/
- Wallet tracking: Etherscan, Dune Analytics
- Smart contract: Polymarket's CLOB (Central Limit Order Book)

**News:**
- Twitter API (X API v2)
- Google News API
- NewsAPI.org
- RSS feeds for major outlets

### Analysis Tools

- **Python libraries:** web3.py, pandas, matplotlib
- **Database:** PostgreSQL with TimescaleDB for time-series
- **Visualization:** Grafana, Plotly
- **Statistical analysis:** scipy, statsmodels

### Similar Projects

- **Unusual Whales** (stock market unusual options activity)
- **Dune Analytics** (blockchain analytics)
- **Nansen** (smart money tracking for crypto)
- **Arkham Intelligence** (on-chain intelligence)

---

## Part 10: Next Steps

### Immediate Actions

1. **Validate Approach:**
   - [ ] Find 3-5 historical examples manually
   - [ ] Calculate basic statistics on price-news correlation
   - [ ] Assess data availability

2. **Legal Review:**
   - [ ] Consult attorney on prediction market trading
   - [ ] Review CFTC guidance on event contracts
   - [ ] Check terms of service for Polymarket API

3. **Community Research:**
   - [ ] Search for existing academic papers
   - [ ] Check if others are building similar tools
   - [ ] Engage with Polymarket community (Discord, Twitter)

### Long-Term Vision

**Possible Outcomes:**

1. **Public Good:** Release free dashboard showing market integrity
2. **Research Paper:** Academic publication on prediction market efficiency
3. **Trading Strategy:** Personal use for informed betting (with caution)
4. **Regulatory Tool:** Offer to CFTC as market surveillance

---

## Appendix: Sample Code Snippets

### Price Change Detection

```python
def detect_anomalous_moves(market_id, threshold=0.10, window_minutes=60):
    """
    Detect significant price moves without news catalysts
    """
    prices = get_market_prices(market_id, interval='1m')
    
    anomalies = []
    for i in range(window_minutes, len(prices)):
        current_price = prices[i]
        past_price = prices[i - window_minutes]
        
        change = (current_price - past_price) / past_price
        
        if abs(change) >= threshold:
            # Check for news in preceding hour
            news = search_news(
                topic=get_market_topic(market_id),
                start=prices.index[i - window_minutes],
                end=prices.index[i]
            )
            
            if not news:
                anomalies.append({
                    'timestamp': prices.index[i],
                    'change': change,
                    'price': current_price,
                    'volume': get_volume(market_id, prices.index[i])
                })
    
    return anomalies
```

### Wallet Tracking

```python
def analyze_wallet_performance(wallet_address, min_trades=10):
    """
    Calculate performance metrics for a wallet
    """
    trades = get_wallet_trades(wallet_address)
    
    if len(trades) < min_trades:
        return None
    
    early_entries = 0
    total_trades = 0
    total_pnl = 0
    
    for trade in trades:
        market = get_market(trade.market_id)
        
        # Was this an "early" entry?
        time_to_resolution = market.resolved_at - trade.timestamp
        if time_to_resolution > 24 * 3600:  # More than 24h early
            early_entries += 1
        
        # Calculate P&L
        if trade.outcome == market.final_outcome:
            total_pnl += trade.size * (1/trade.price - 1)
        else:
            total_pnl -= trade.size
        
        total_trades += 1
    
    return {
        'address': wallet_address,
        'total_trades': total_trades,
        'early_entry_rate': early_entries / total_trades,
        'total_pnl': total_pnl,
        'roi': total_pnl / sum(t.size for t in trades)
    }
```

---

## Conclusion

Insider trading detection on Polymarket is **technically feasible** through:
1. Real-time price monitoring for >10% moves
2. News correlation analysis (1-48h post-move)
3. Blockchain wallet tracking for repeat patterns
4. Statistical backtesting on historical data

**Legal status:** Gray area. Following public patterns likely legal, but using your own insider info is not.

**Ethical verdict:** Research and transparency efforts are positive. Pure profit-seeking from insider detection requires careful ethical consideration.

**Recommended approach:** Start with backtesting, publish findings openly, contribute to market integrity research before any trading applications.

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-07  
**Status:** Research complete, awaiting implementation decision
