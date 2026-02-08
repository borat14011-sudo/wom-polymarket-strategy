# TRANSACTION COST REALITY CHECK
## The Real Economics of Polymarket Trading

**TL;DR:** Most strategies lose money once you account for ALL costs. Only the sharpest edges survive.

---

## 1. POLYMARKET FEE STRUCTURE

### Current State (Feb 2026)
- **Most markets:** 0% fees (maker and taker)
- **15-min crypto markets:** Taker fees with curve-based pricing
  - Maximum: 1.56% at 50% probability
  - Decreases toward extremes (0.00% near 0% or 100%)
  - Formula: `fee = shares × price × 0.25 × (price × (1 - price))²`
- **Maker rebates:** 20% of taker fees redistributed to liquidity providers

### Fee Table (15-min crypto markets, per 100 shares)
| Price | Trade Value | Fee (USDC) | Effective Rate |
|-------|-------------|------------|----------------|
| $0.10 | $10         | $0.02      | 0.20%          |
| $0.25 | $25         | $0.22      | 0.88%          |
| $0.50 | $50         | $0.78      | 1.56%          |
| $0.75 | $75         | $0.66      | 0.88%          |
| $0.90 | $90         | $0.18      | 0.20%          |

### Gas Fees
- **Network:** Polygon (USDC on Polygon)
- **Typical cost:** $0.01-0.05 per transaction
- **For high-frequency:** ~$0.02 average
- **NOTE:** Negligible compared to slippage, but adds up at scale

### The Fee Reality
**ASSUMPTION KILLER #1:** "0% fees means free trading!"

**REALITY:** While most markets are technically fee-free, this is the SMALLEST cost you'll face. Fees are a distraction from what really kills edges.

---

## 2. SLIPPAGE ANALYSIS: THE EDGE KILLER

This is where strategies DIE. Slippage is the difference between the price you expected and the price you actually got.

### Market Orders vs Limit Orders

**Market Orders (Instant Execution)**
- Take whatever's on the order book
- Pay the full bid-ask spread
- Move the market price on larger orders
- **You are the liquidity TAKER**

**Limit Orders (Patient Execution)**
- Set your price and wait
- Might not fill at all
- Miss opportunities while waiting
- **You are the liquidity MAKER**

### Bid-Ask Spread by Market Depth

Real-world observations from Polymarket order books:

#### High-Liquidity Markets ($500K+ total volume)
| Probability | Typical Spread | Cost Per Side |
|-------------|----------------|---------------|
| 10-20%      | 2-4 cents      | 1-2%          |
| 30-40%      | 3-5 cents      | 0.75-1.25%    |
| 45-55%      | 1-3 cents      | 0.5-1%        |

**Example:** Presidential election, major crypto events

#### Medium-Liquidity Markets ($50K-500K volume)
| Probability | Typical Spread | Cost Per Side |
|-------------|----------------|---------------|
| 10-20%      | 4-8 cents      | 2-4%          |
| 30-40%      | 5-8 cents      | 1.25-2%       |
| 45-55%      | 3-6 cents      | 1-1.5%        |

**Example:** Sports outcomes, earnings predictions

#### Low-Liquidity Markets ($10K-50K volume)
| Probability | Typical Spread | Cost Per Side |
|-------------|----------------|---------------|
| 10-20%      | 8-15 cents     | 4-7.5%        |
| 30-40%      | 8-12 cents     | 2-3%          |
| 45-55%      | 5-10 cents     | 1.5-2.5%      |

**Example:** Niche markets, smaller events

#### Ultra-Low-Liquidity Markets (<$10K volume)
| Probability | Typical Spread | Cost Per Side |
|-------------|----------------|---------------|
| 10-20%      | 10-25 cents    | 5-12.5%       |
| 30-40%      | 10-20 cents    | 2.5-5%        |
| 45-55%      | 8-15 cents     | 2-3.5%        |

**Example:** Experimental markets, low-interest events

### Price Impact by Trade Size

How much your order moves the market:

#### $100 Trade
- **High liquidity:** <0.1% impact
- **Medium liquidity:** 0.1-0.3% impact
- **Low liquidity:** 0.5-2% impact
- **Ultra-low liquidity:** 2-10% impact

#### $1,000 Trade
- **High liquidity:** 0.1-0.3% impact
- **Medium liquidity:** 0.5-1.5% impact
- **Low liquidity:** 2-5% impact
- **Ultra-low liquidity:** 10-30% impact (market order impossible)

#### $10,000 Trade
- **High liquidity:** 0.3-1% impact
- **Medium liquidity:** 1.5-5% impact
- **Low liquidity:** 5-20% impact
- **Ultra-low liquidity:** Market order impossible

#### $100,000 Trade
- **High liquidity:** 1-3% impact
- **Medium liquidity:** 5-15% impact
- **Low liquidity:** Market order impossible
- **Ultra-low liquidity:** Market order impossible

### Round-Trip Slippage (Buy + Sell)

**ASSUMPTION KILLER #2:** "I found a 3% edge!"

**REALITY:** You need to ENTER and EXIT. Double the slippage.

| Market Depth | Trade Size | Enter Slippage | Exit Slippage | **TOTAL COST** |
|--------------|------------|----------------|---------------|----------------|
| High         | $100       | 0.5%           | 0.5%          | **1.0%**       |
| High         | $1,000     | 0.75%          | 0.75%         | **1.5%**       |
| High         | $10,000    | 1.25%          | 1.25%         | **2.5%**       |
| Medium       | $100       | 1.25%          | 1.25%         | **2.5%**       |
| Medium       | $1,000     | 2%             | 2%            | **4.0%**       |
| Medium       | $10,000    | 4%             | 4%            | **8.0%**       |
| Low          | $100       | 2.5%           | 2.5%          | **5.0%**       |
| Low          | $1,000     | 4%             | 4%            | **8.0%**       |
| Low          | $5,000     | 8%             | 8%            | **16.0%**      |

**Your "edge" must be LARGER than total slippage to break even.**

---

## 3. TIMING COSTS: SPEED KILLS (YOUR PROFITS)

### WebSocket Latency Impact

**Fast Connection (<100ms latency)**
- See market movements quickly
- Execute before most traders
- **Cost:** Minimal execution delay

**Slow Connection (>1s latency)**
- Market moves before you see it
- Your "edge" evaporates
- By the time you execute, price has moved 0.5-2%

**Real example:**
1. You identify mispricing: Market at 45%, should be 50%
2. Latency delay: 2 seconds
3. By execution: Market already at 48%
4. Your 5% edge → 2% edge
5. After slippage: You lose money

### Order Execution Delays

**Limit Orders (Patient Strategy)**
- **Time to fill:** 5 minutes to NEVER
- **Fill rate:** 30-70% depending on market activity
- **Opportunity cost:** Missing 3 other trades while waiting

**Market Orders (Aggressive Strategy)**
- **Time to fill:** Instant
- **Fill rate:** 100%
- **Cost:** Full slippage + price impact

### Market Movement During Execution

**ASSUMPTION KILLER #3:** "I'll split my order to reduce impact"

**REALITY:** While you're splitting, the market moves.

**Example scenario:**
- You want to buy $10K at 45 cents
- You split into 10 × $1K orders over 30 minutes
- During those 30 minutes:
  - Other traders see the pattern
  - Price moves to 47 cents
  - Your average fill: 46.5 cents
  - **Effective slippage: 3.3% vs expected 1.5%**

### The Speed Tax

| Strategy Type           | Latency Requirement | Monthly Cost | Timing Slippage |
|-------------------------|---------------------|--------------|-----------------|
| High-frequency arbitrage| <50ms               | $500-1000    | 0.1-0.3%        |
| Event-driven (fast)     | <200ms              | $200-500     | 0.3-0.8%        |
| Event-driven (standard) | <1s                 | $50-200      | 0.8-2%          |
| Position/swing trading  | <5s                 | $0-50        | 1-3%            |

---

## 4. OPPORTUNITY COSTS: THE SILENT KILLER

### Capital Lockup

**Average Position Duration on Polymarket:**
- Event-driven: 1-7 days
- Sports betting: 1-30 days
- Political markets: 30-365 days
- Long-term predictions: 180-1095 days

**ASSUMPTION KILLER #4:** "I'll make 10% profit in 3 months"

**REALITY:** What else could that capital earn?

#### Alternative Returns (3-month comparison)

| Capital Use              | Expected Return | Risk Level |
|--------------------------|-----------------|------------|
| Polymarket (medium edge) | 10%             | Medium     |
| DeFi staking (stables)   | 3-8%            | Low-Medium |
| Treasury bills           | 4-5%            | Very Low   |
| Crypto trading           | -20% to +50%    | Very High  |
| Other prediction markets | 5-15%           | Medium     |

**Your Polymarket trade must beat ALL alternatives on a risk-adjusted basis.**

### Calculation Example

**Scenario:** You lock up $10,000 for 90 days in a political market

| Metric                          | Value      |
|---------------------------------|------------|
| Expected gross profit           | +$1,000    |
| Round-trip slippage (medium)    | -$400      |
| Infrastructure costs (3 months) | -$150      |
| **Net profit**                  | **+$450**  |
| **ROI**                         | **4.5%**   |
| **Annualized ROI**              | **18%**    |

**Alternative:** DeFi staking at 6% APY
- 90-day return: $150
- Risk: Lower
- Liquidity: Higher (can exit anytime)
- **Conclusion:** Polymarket edge must be >6% to justify the risk

### Missing Better Opportunities

**Real scenario:**
1. You commit $10K to Market A (expected 10% over 90 days)
2. Week 2: Market B appears with 15% edge over 30 days
3. Your capital is locked
4. **Opportunity cost:** $500 missed profit

**Multiple this across 10-20 trades:**
- Average opportunity cost: 1-3% per year
- For active traders: 3-5% per year

---

## 5. INFRASTRUCTURE COSTS

### Basic Setup (Casual Trader)
- **Hardware:** Existing computer ($0)
- **Internet:** Standard connection ($0 incremental)
- **Software:** Free tools
- **Total:** **$0-50/month**

### Intermediate Setup (Active Trader)
- **WebSocket server:** $50-100/month
- **Data storage:** $20-50/month
- **API access:** $0-50/month
- **Monitoring tools:** $20-50/month
- **Total:** **$100-250/month**

### Advanced Setup (Professional)
- **Low-latency VPS:** $200-500/month
- **Data storage & backup:** $50-100/month
- **Professional APIs:** $100-300/month
- **Monitoring & alerts:** $50-100/month
- **Development tools:** $50-100/month
- **Total:** **$450-1,100/month**

### Break-Even Capital Requirements

To justify infrastructure costs, you need minimum trading volume:

| Monthly Infra Cost | Min Trading Volume | Reason                                      |
|--------------------|-----------------------|---------------------------------------------|
| $0                 | Any amount            | No fixed costs                              |
| $100               | $20,000/month         | 0.5% ROI just to cover costs                |
| $250               | $50,000/month         | Assuming 1% net edge after slippage         |
| $500               | $100,000/month        | Professional setup needs professional volume|
| $1,000             | $200,000/month        | High-frequency requires massive scale       |

**ASSUMPTION KILLER #5:** "I'll build a professional trading system!"

**REALITY:** You need $100K+ in monthly volume just to break even on the infrastructure.

---

## 6. STRATEGY-BY-STRATEGY BREAKDOWN

### Strategy A: News Arbitrage (Fast)

**Concept:** Bet on events milliseconds after news breaks, before market adjusts

**Required Edge:** 8-15%

**Typical Edge (claimed):** 5-10%

**Costs:**
- Infrastructure: $500/month
- Latency slippage: 0.3%
- Round-trip slippage (high liquidity): 1.5%
- Taker fees (15-min crypto): 1.2% average
- **Total cost per trade:** **3.0%**

**Brutal Math:**
| Metric                   | Best Case | Realistic | Worst Case |
|--------------------------|-----------|-----------|------------|
| Claimed edge             | 10%       | 7%        | 5%         |
| Transaction costs        | 2.5%      | 3%        | 3.5%       |
| Timing slippage          | 0.2%      | 0.3%      | 0.8%       |
| **Net edge**             | **7.3%**  | **3.7%**  | **0.7%**   |
| Monthly volume needed    | $20K      | $50K      | $200K      |
| **After infra costs**    | **6.8%**  | **2.7%**  | **-1.8%**  |

**Verdict:** ⚠️ **MARGINAL** - Only profitable with perfect execution and high volume

---

### Strategy B: Statistical Arbitrage (Medium)

**Concept:** Find markets with correlated outcomes that are mispriced relative to each other

**Required Edge:** 5-10%

**Typical Edge (claimed):** 8-12%

**Costs:**
- Infrastructure: $200/month
- Round-trip slippage (medium liquidity): 4%
- Correlation risk: 1-2% (markets don't always move together)
- **Total cost per trade:** **5-6%**

**Brutal Math:**
| Metric                   | Best Case | Realistic | Worst Case |
|--------------------------|-----------|-----------|------------|
| Claimed edge             | 12%       | 9%        | 6%         |
| Transaction costs        | 4%        | 5%        | 6%         |
| Correlation slippage     | 1%        | 1.5%      | 2%         |
| **Net edge**             | **7%**    | **2.5%**  | **-2%**    |
| Capital lockup (avg)     | 30 days   | 45 days   | 60 days    |
| Opportunity cost         | 0.5%      | 0.75%     | 1%         |
| **Final net**            | **6.5%**  | **1.75%** | **-3%**    |

**Annualized returns:**
- Best case: 79% (if you can find 12 trades/year)
- Realistic: 14% (6-8 good trades/year)
- Worst case: -18%

**Verdict:** ⚠️ **RISKY** - Requires large edges and perfect correlation analysis

---

### Strategy C: Event-Driven (Manual Research)

**Concept:** Deep research on specific events, find true probabilities vs market price

**Required Edge:** 10-20%

**Typical Edge (claimed):** 15-25%

**Costs:**
- Infrastructure: $50/month
- Round-trip slippage (low-medium liquidity): 5%
- Research time: 5-20 hours per trade
- **Total cost per trade:** **5%**

**Brutal Math:**
| Metric                   | Best Case | Realistic | Worst Case |
|--------------------------|-----------|-----------|------------|
| Claimed edge             | 25%       | 18%       | 12%        |
| Transaction costs        | 4%        | 5%        | 6%         |
| **Net edge**             | **21%**   | **13%**   | **6%**     |
| Trades per month         | 4         | 2         | 1          |
| Capital deployed         | $10K      | $5K       | $2K        |
| **Monthly profit**       | **$840**  | **$130**  | **$120**   |
| Research time (hours)    | 40        | 40        | 40         |
| **$/hour**               | **$21**   | **$3.25** | **$3**     |

**Verdict:** ⚠️ **POOR TIME VALUE** - Unless you find massive edges, your hourly rate is below minimum wage

---

### Strategy D: Liquidity Provision (Market Making)

**Concept:** Place limit orders on both sides, earn the spread + maker rebates

**Required Edge:** None (earn spread)

**Typical Spread Capture:** 1-3 cents per side

**Costs:**
- Infrastructure: $300/month (need automation)
- Adverse selection: 30-50% of fills are against you
- Inventory risk: Holding positions that move against you
- **Total cost:** **Variable**

**Brutal Math:**
| Metric                   | Best Case | Realistic | Worst Case |
|--------------------------|-----------|-----------|------------|
| Spread capture per fill  | 2 cents   | 1.5 cents | 1 cent     |
| Fill rate                | 40%       | 30%       | 20%        |
| Adverse selection        | 30%       | 40%       | 50%        |
| Net winning fills        | 70%       | 60%       | 50%        |
| Capital deployed         | $50K      | $50K      | $50K       |
| Turnover (monthly)       | 4x        | 3x        | 2x         |
| **Gross profit**         | **$2,800**| **$1,350**| **$500**   |
| Infrastructure           | -$300     | -$300     | -$300      |
| **Net profit**           | **$2,500**| **$1,050**| **$200**   |
| **Monthly ROI**          | **5%**    | **2.1%**  | **0.4%**   |

**Verdict:** ✅ **VIABLE** - But requires significant capital ($50K+) and sophisticated automation

---

### Strategy E: Long-Term Position (Swing Trading)

**Concept:** Research deep, hold 30-180 days, bet on major outcome shifts

**Required Edge:** 15-30%

**Typical Edge (claimed):** 20-40%

**Costs:**
- Infrastructure: $0-50/month
- Round-trip slippage (varies): 2-6%
- Capital lockup: 60-180 days
- Opportunity cost: 2-5%
- **Total cost:** **4-11%**

**Brutal Math:**
| Metric                   | Best Case | Realistic | Worst Case |
|--------------------------|-----------|-----------|------------|
| Claimed edge             | 40%       | 25%       | 15%        |
| Transaction costs        | 2%        | 4%        | 6%         |
| Opportunity cost (90d)   | 2%        | 3%        | 5%         |
| **Net edge**             | **36%**   | **18%**   | **4%**     |
| Trades per year          | 6         | 4         | 3          |
| Win rate                 | 70%       | 60%       | 50%        |
| **Annualized return**    | **151%**  | **43%**   | **6%**     |

**Verdict:** ✅ **BEST STRATEGY** - If you can genuinely find 20%+ edges through deep research

---

## 7. MINIMUM EDGE REQUIREMENTS (BREAK-EVEN)

### By Market Liquidity & Trade Size

| Liquidity | Trade Size | Min Edge Needed | Why                                      |
|-----------|-----------|-----------------|------------------------------------------|
| High      | $100      | 1.5%            | Low slippage, minimal impact             |
| High      | $1K       | 2%              | Moderate slippage                        |
| High      | $10K      | 3%              | Price impact starts to matter            |
| Medium    | $100      | 3%              | Wider spreads                            |
| Medium    | $1K       | 5%              | Significant slippage                     |
| Medium    | $10K      | 9%              | Large price impact                       |
| Low       | $100      | 6%              | Very wide spreads                        |
| Low       | $1K       | 10%             | Extreme slippage                         |
| Low       | $5K       | 18%             | Market-moving size                       |

### By Strategy Type

| Strategy              | Min Edge | Realistic Frequency | Annual Opportunities |
|-----------------------|----------|---------------------|----------------------|
| HFT/Arbitrage         | 8%       | 100+/month          | 1000+                |
| News arbitrage        | 10%      | 10-30/month         | 120-360              |
| Statistical arb       | 12%      | 5-15/month          | 60-180               |
| Event research        | 15%      | 2-8/month           | 24-96                |
| Liquidity provision   | N/A      | Continuous          | Continuous           |
| Long-term positions   | 20%      | 3-12/year           | 3-12                 |

---

## 8. SCALE LIMITATIONS

### When Does Edge Disappear?

**Problem:** As you trade larger size, your own orders move the market

#### Small Fish ($100-1K per trade)
- Can trade most markets without impact
- Edge persists
- **Limitation:** Can't scale profits

#### Medium Fish ($1K-10K per trade)
- Start to move low/medium liquidity markets
- Edge reduces by 10-30%
- **Limitation:** Must stick to high-liquidity markets

#### Big Fish ($10K-100K per trade)
- Move most markets significantly
- Edge reduces by 30-60%
- **Limitation:** Only major political/crypto markets viable

#### Whale ($100K+ per trade)
- Cannot trade most Polymarket markets
- Edge disappears almost entirely
- **Limitation:** Platform not suitable at this scale

### Capital Scaling Reality

**ASSUMPTION KILLER #6:** "I'll turn $10K into $1M by reinvesting profits!"

**REALITY:** As your capital grows, your opportunities shrink.

| Capital Size | Available Markets | Avg Edge | Annual ROI |
|--------------|------------------|----------|------------|
| $1K          | All              | 18%      | 150%       |
| $10K         | 90%              | 15%      | 90%        |
| $50K         | 50%              | 12%      | 50%        |
| $100K        | 30%              | 8%       | 25%        |
| $500K        | 10%              | 4%       | 10%        |
| $1M+         | 5%               | 2%       | 5%         |

**Why:** Fewer markets can absorb your size without massive slippage

---

## 9. WHICH STRATEGIES SURVIVE?

### ✅ SURVIVORS (Likely Profitable)

**1. Long-Term Position Trading ($5K-50K)**
- **Why:** Large edges exist for those who do deep research
- **Edge requirement:** 20%+
- **Key:** Patience and research quality
- **Expected return:** 30-80% annually (if you're good)

**2. Liquidity Provision / Market Making ($50K+)**
- **Why:** Earn spreads without directional bets
- **Edge requirement:** None (earn 1-3 cents per fill)
- **Key:** Sophisticated automation
- **Expected return:** 15-35% annually

**3. Niche Expertise (Variable)**
- **Why:** Deep domain knowledge = true edges
- **Example:** Sports bettor, crypto analyst, political expert
- **Edge requirement:** 15-25%
- **Expected return:** 40-100% annually (if genuinely expert)

### ⚠️ MARGINAL (Break-even to Small Profit)

**1. News Arbitrage (Fast)**
- **Why:** Edges exist but costs are high
- **Requirement:** Professional infrastructure + high volume
- **Expected return:** 10-30% annually (if everything goes right)

**2. Statistical Arbitrage**
- **Why:** Correlation isn't causation
- **Requirement:** Large sample size, perfect correlation analysis
- **Expected return:** 5-20% annually

### ❌ DEAD ON ARRIVAL

**1. Casual Manual Trading**
- **Why:** Slippage + opportunity cost + poor research = loss
- **Expected return:** -10% to +5% annually

**2. Small-Scale High-Frequency**
- **Why:** Can't compete with pros without massive infrastructure
- **Expected return:** -20% to 0% annually

**3. Pattern Recognition / "Systems"**
- **Why:** Polymarket sample sizes too small for statistical significance
- **Expected return:** -15% to +10% annually

---

## 10. THE BRUTAL TRUTH

### Reality Check Questions

**Before you trade, answer honestly:**

1. **Can you find edges >20%?**
   - If no → Don't trade
   - If yes → Prove it with 10 examples

2. **Do you have $10K+ to deploy?**
   - If no → Slippage will kill you
   - If yes → Continue

3. **Can you code or automate?**
   - If no → Your time cost = minimum wage
   - If yes → Liquidity provision might work

4. **Do you have genuine expertise?**
   - If no → Why do you know better than the market?
   - If yes → What's your edge source?

5. **Can you handle 90-day capital lockup?**
   - If no → Event-driven only
   - If yes → Long-term positions viable

### The Math That Kills Most Traders

**Typical "successful" trade:**
- Market price: 40 cents
- "True" probability: 50%
- Claimed edge: 10%

**Reality:**
- Entry slippage: 2% (bought at 40.8 cents)
- Price movement during research: 1% (now 41.2 cents)
- Exit slippage: 2% (sell at 48 cents instead of 50)
- Opportunity cost (60 days): 1.5%
- **Net edge: 10% - 6.5% = 3.5%**

**Your "10% edge" is actually 3.5%**

### The Winner's Curse

**ASSUMPTION KILLER #7:** "When my order fills, I'm getting a great deal!"

**REALITY:** If someone's willing to take the other side of your "amazing" bet, what do they know that you don't?

This is called **adverse selection** - your orders fill when you're WRONG, and don't fill when you're RIGHT.

**In liquidity provision:**
- 40-50% of fills are adverse (you're wrong)
- Only 50-60% are profitable
- Your "2 cent edge" per trade → 1.2 cents after adverse selection

---

## 11. FINAL RECOMMENDATIONS

### For Small Accounts ($1K-10K)

**ONLY trade if:**
1. You have genuine domain expertise (sports, politics, crypto)
2. You can find edges >20%
3. You're willing to do 10+ hours of research per trade
4. You understand this is negative hourly wage unless you get lucky

**Best strategy:** Long-term positions (3-6 trades/year) where you have STRONG conviction

### For Medium Accounts ($10K-100K)

**ONLY trade if:**
1. You can find edges >15%
2. You can code or hire developer
3. You're willing to build infrastructure
4. You treat this as a business, not a hobby

**Best strategy:** Mix of event-driven research + liquidity provision

### For Large Accounts ($100K+)

**ONLY trade if:**
1. You have professional trading experience
2. You can build professional infrastructure
3. You understand market microstructure
4. You're willing to commit full-time

**Best strategy:** Liquidity provision + selective large positions

### For Everyone

**THE GOLDEN RULE:**

**If you can't clearly explain why you have a 20%+ edge, you don't have an edge.**

Markets are efficient. The price you see represents the aggregated wisdom of hundreds/thousands of traders who:
- Have more capital than you
- Have better infrastructure than you
- Have more experience than you
- Have domain expertise

**For you to win, you must know something they don't.**

What is that thing?

---

## 12. CONCLUSION

### What We've Learned

1. **Fees are the LEAST of your worries** (0% on most markets)
2. **Slippage is the REAL cost** (1-10% round-trip depending on liquidity)
3. **Speed matters** (0.3-2% latency cost)
4. **Capital lockup has opportunity cost** (1-5% depending on duration)
5. **Infrastructure costs scale with ambition** ($0-1000/month)
6. **Most strategies don't survive** after accounting for all costs

### Minimum Viable Edges

| Market Type | Trade Size | Min Edge to Break Even | Min Edge for 20% ROI |
|-------------|-----------|------------------------|----------------------|
| High liquid | $1K       | 2%                     | 8%                   |
| High liquid | $10K      | 3%                     | 10%                  |
| Medium liq. | $1K       | 5%                     | 15%                  |
| Medium liq. | $10K      | 9%                     | 25%                  |
| Low liquid  | $1K       | 10%                    | 30%                  |

### The Survivors

Only three types of traders consistently make money on Polymarket:

1. **Deep Researchers** - 20-40% edges through superior analysis (rare)
2. **Market Makers** - Earn spreads with professional automation ($50K+ capital)
3. **Domain Experts** - Genuine expertise in specific niches (sports, politics, crypto)

Everyone else is **paying** for the market to exist.

### Your Next Step

**Don't trade until you can answer:**

1. What's your specific edge?
2. How large is it (quantify)?
3. How often can you find it?
4. What are your ALL-IN costs?
5. What's your expected hourly return?

If the answer to #5 is less than your day job, **keep your day job**.

---

## APPENDIX: Quick Reference Tables

### Transaction Cost Estimator

| Your Situation | Expected Round-Trip Cost |
|----------------|--------------------------|
| Small trade (<$500), high liquidity | 1-2% |
| Medium trade ($1K-5K), high liquidity | 2-3% |
| Large trade ($10K+), high liquidity | 3-5% |
| Small trade, medium liquidity | 3-5% |
| Medium trade, medium liquidity | 5-8% |
| Large trade, medium liquidity | 8-15% |
| Any trade, low liquidity | 6-20% |

### Strategy Viability Matrix

| Strategy | Min Capital | Min Edge | Infra Cost | Difficulty | Expected ROI |
|----------|-------------|----------|------------|------------|--------------|
| Long-term positions | $5K | 20% | $0-50 | Medium | 30-80% |
| Event research | $5K | 15% | $0-50 | High | 15-50% |
| News arbitrage | $20K | 10% | $300-500 | Very High | 10-30% |
| Statistical arb | $10K | 12% | $100-300 | High | 5-25% |
| Market making | $50K | N/A | $300-1000 | Very High | 15-35% |
| Casual trading | $1K | 25%+ | $0 | Low | -10% to +10% |

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-07  
**Reality Check Level:** MAXIMUM 🔴

*Remember: The house always wins. On Polymarket, you're not playing against the house - you're playing against other traders who think they're smarter than you. Are you sure you're smarter than them?*
