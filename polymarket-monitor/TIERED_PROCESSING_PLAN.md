# TIERED PROCESSING PLAN - Cost-Efficient 2-Year Backtest

**Philosophy:** Assembly line processing - Python → Haiku → Sonnet → Opus

**Goal:** Analyze 10,000+ markets from Feb 2024-2026 for <$20 total cost

---

## 🎯 TIER 1: Data Collection (Python - $0)

**Task:** Dumb data pulls, no AI needed

**Process:**
```python
historical_2yr_scraper.py
├── Fetch all markets from Gamma API (Feb 2024+)
├── Fetch price histories from CLOB API
├── Downsample to 4 prices/day (00:00, 06:00, 12:00, 18:00 UTC)
└── Save raw JSON (~500MB)
```

**Output:** `markets_raw_2yr.json`
- 10,000+ markets
- 4 prices/day × 730 days = 2,920 data points per market
- Market metadata (question, dates, volume, outcome)

**Cost:** $0 (pure API calls, no AI)
**Time:** 2-4 hours (rate-limited scraping)

---

## 🎯 TIER 2: Market Categorization (Sonnet - $5-8)

**Task:** Tag each market with event type + extract features

**Agents:** 20 Sonnet agents running in parallel
- Each agent gets 500 markets
- 10,000 markets ÷ 20 agents = 500 markets/agent

**Per-Market Analysis (Sonnet):**
```
Input: Market question + metadata
Output: {
  "category": "government_shutdown",
  "subcategory": "threat",
  "keywords": ["congress", "budget", "funding"],
  "sentiment": "fear",
  "timeframe": "short" | "medium" | "long",
  "volatility": 0.45,
  "hype_pattern": "spike_fade" | "steady" | "random"
}
```

**Parallelization:**
- Max 20 agents (API-safe, won't crash)
- Each processes sequentially (no internal parallelism)
- Total throughput: ~100 markets/minute
- 10K markets = ~100 minutes

**Cost Estimate:**
- Sonnet: ~$0.015 per 1K input tokens
- Per market: ~200 tokens in + 100 tokens out = $0.0045
- 10,000 markets × $0.0045 = **$45**
- With caching: ~$8-10

**Output:** `markets_categorized.json`

---

## 🎯 TIER 3: Pattern Detection (Sonnet - $2-5)

**Task:** Find repeating patterns within each category

**Agents:** 14 Sonnet agents (one per category)
- Government (shutdowns, debt ceiling)
- Trump (indictments, trials, elections)
- Crypto (ETF, exchanges, regulations)
- Weather (temperature, storms)
- Sports (upsets, favorites)
- Tech/Musk (tweets, products)
- International (wars, sanctions)
- Elections (primary, general)
- Economy (jobs, inflation)
- Health (pandemic, FDA)
- Entertainment (awards, box office)
- Science (launches, discoveries)
- Crime (trials, verdicts)
- Other

**Per-Category Analysis (Sonnet):**
```
Input: All markets in category (e.g., 280 Musk markets)
Output: {
  "patterns_found": [
    {
      "name": "MUSK_FADE_EXTREMES",
      "description": "Tweet count extremes (0-19 or 200+) never hit",
      "frequency": 68,
      "win_rate": 0.971,
      "confidence": "high"
    }
  ],
  "market_behavior": "...",
  "recommended_strategy": "..."
}
```

**Cost Estimate:**
- 14 categories × 500-1000 markets each
- Per category: ~50K tokens in, ~2K tokens out
- $0.15-0.35 per category
- Total: **$2-5**

**Output:** `category_patterns.json`

---

## 🎯 TIER 4: Strategy Synthesis (Opus - $3-8)

**Task:** Take all category findings and build final strategies

**Agents:** 1 Opus agent with ultrathink

**Input:**
- All 14 category pattern reports
- Cross-category correlations
- Historical win rates
- Market taxonomy

**Opus Analysis:**
```
1. Identify strongest patterns (>70% win rate, >50 trades)
2. Cross-validate between categories
3. Build walk-forward backtest (2024 train → 2025 test)
4. Create production-ready strategies
5. Risk assessment and position sizing
6. Edge durability analysis
```

**Output:**
- `FINAL_STRATEGY_REPORT.md` (comprehensive)
- `production_strategies.json` (deploy-ready)
- Walk-forward validation results
- Risk management guidelines

**Cost Estimate:**
- Opus with high thinking
- ~100K tokens in (all category reports)
- ~5K tokens out (synthesis)
- **$3-8 total**

---

## 📊 TOTAL COST BREAKDOWN

| Tier | Model | Markets | Cost |
|------|-------|---------|------|
| 1. Data Pull | Python | 10,000 | $0 |
| 2. Categorization | Sonnet (20 agents) | 10,000 | $8-10 |
| 3. Pattern Detection | Sonnet (14 agents) | 14 categories | $2-5 |
| 4. Strategy Synthesis | Opus (1 agent) | Final | $3-8 |
| **TOTAL** | | | **$13-23** |

**Compare to naive approach:**
- Running Opus on every market: 10,000 × $0.15 = **$1,500** 😱
- Our approach: **65-115x cheaper** ✅

---

## ⚡ EXECUTION PLAN

### Phase 1: Data Collection (2-4 hours)
```bash
python historical_2yr_scraper.py
# Output: markets_raw_2yr.json (~500MB)
```

### Phase 2: Categorization (2 hours)
```python
# Spawn 20 Sonnet agents
for batch in chunks(markets, 500):
    spawn_agent(
        model="sonnet",
        task=f"Categorize {len(batch)} markets",
        data=batch
    )
# Output: markets_categorized.json
```

### Phase 3: Pattern Detection (30 min)
```python
# Spawn 14 Sonnet agents (one per category)
for category, markets in group_by_category(data):
    spawn_agent(
        model="sonnet",
        task=f"Find patterns in {category}",
        data=markets
    )
# Output: category_patterns.json
```

### Phase 4: Strategy Synthesis (15 min)
```python
# Single Opus agent
spawn_agent(
    model="opus",
    thinking="high",
    task="Synthesize all findings into final strategies",
    data=all_category_reports
)
# Output: FINAL_STRATEGY_REPORT.md + production_strategies.json
```

**Total Time:** 5-7 hours (mostly waiting for data scraping)

---

## 🚀 API RATE LIMIT SAFETY

**Tier 1 (Python scraping):**
- 0.1s delay between requests
- ~10 requests/second
- Well within Polymarket limits

**Tier 2 (20 Sonnet agents):**
- Each agent processes sequentially (no bursting)
- 20 parallel streams = safe
- Anthropic API handles this easily

**Tier 3 (14 Sonnet agents):**
- Fewer agents, larger payloads
- No rate limit risk

**Tier 4 (1 Opus agent):**
- Single agent = zero risk

**Safety Factor:** 10x below typical rate limits ✅

---

## 💡 OPTIMIZATION TRICKS

**1. Prompt Caching (Sonnet Tier 2)**
- Cache category definitions
- Reuse across all markets
- Saves ~40% on costs

**2. Batch Processing**
- Group similar markets together
- Reduce context switching

**3. Early Termination**
- If category has <20 markets, skip pattern detection
- Focus on high-volume categories

**4. Incremental Saving**
- Checkpoint every 1,000 markets
- Resume if interrupted
- Don't lose progress

---

## 📈 EXPECTED OUTCOMES

**After Tier 2 (Categorization):**
- Know exactly which categories exist
- Market distribution by type
- Initial hype pattern identification

**After Tier 3 (Pattern Detection):**
- 10-20 candidate strategies
- Win rates, sample sizes
- Category-specific insights

**After Tier 4 (Synthesis):**
- 3-5 production-ready strategies
- Walk-forward validated
- Deployment instructions
- Risk management rules

---

## 🎯 SUCCESS METRICS

**Data Quality:**
- ✅ 80%+ markets successfully categorized
- ✅ 10+ categories with 100+ markets each
- ✅ 5+ patterns with >60% win rate

**Cost Efficiency:**
- ✅ Total cost <$25
- ✅ <$0.003 per market analyzed
- ✅ 60x cheaper than naive Opus approach

**Time Efficiency:**
- ✅ Complete in <8 hours
- ✅ Fully automated after data pull
- ✅ Parallel processing maximized

---

## 🔧 IMPLEMENTATION FILES

**To Create:**
1. `tier2_categorize.py` - Spawns 20 Sonnet agents for categorization
2. `tier3_patterns.py` - Spawns 14 Sonnet agents for pattern detection
3. `tier4_synthesis.py` - Spawns 1 Opus agent for final strategy
4. `orchestrator.py` - Runs all 4 tiers sequentially

**To Reuse:**
1. `historical_2yr_scraper.py` - Already built ✅
2. `event_backtest_system.py` - Template for patterns
3. `production_trading_system.py` - Deployment framework

---

**Status:** Ready to build. Awaiting approval to proceed.
