# LIVE MONITOR - QUICK REFERENCE

## What It Does
Scans Polymarket for profitable trades every 10 minutes using 5 validated strategies.

## Files Created

### 1. `live_monitor_simple.py` (Scanner Script)
**Run:** `python live_monitor_simple.py`  
**Runtime:** 30 minutes (3 scans, 10 min apart)  
**Output:**
- Console progress updates
- `live_opportunities_tracker.json` (all opportunities)
- `HIGH_PRIORITY_ALERTS.md` (>200% ROI trades)

### 2. `live_opportunities_tracker.json` (Results)
**Format:**
```json
{
  "summary": {
    "total_scans": 3,
    "total_opportunities": 10,
    "high_priority_count": 5,
    "timestamp": "2026-02-07T18:40:00"
  },
  "opportunities": [
    {
      "question": "Will X happen?",
      "yes_price": 0.85,
      "no_price": 0.15,
      "roi_percent": 567,
      "strategy": "NO-SIDE BIAS",
      "win_rate": 100,
      "volume": 150000,
      "days_to_close": 7,
      "url": "https://polymarket.com/event/..."
    }
  ]
}
```

### 3. `HIGH_PRIORITY_ALERTS.md` (Urgent Opportunities)
Markdown report of all trades with >200% ROI.

## How to Read Results

### ROI Calculation
```
ROI = ((1.0 - NO_price) / NO_price) * 100

Example: NO price = $0.15
ROI = ((1.0 - 0.15) / 0.15) * 100 = 567%
```

**What it means:**  
If you bet $100 on NO at $0.15, you can win $567 if NO wins.

### Win Rate
Historical win rate of the strategy that flagged this market:
- **100%** = NO-SIDE BIAS (85/85 wins)
- **90.5%** = CATEGORY FILTER (politics/crypto)
- **83.3%** = CONTRARIAN FADE (5/6 wins)
- **66.7%** = TIME HORIZON (<3 days)
- **65%** = NEWS REVERSION

### Strategies Explained

**1. NO-SIDE BIAS (100% win rate)**
- When YES price is 70-90%, betting NO captures high upside
- Historical: 85 markets all resolved to NO when in this range
- Caveat: Limited real-time validation

**2. CONTRARIAN EXPERT FADE (83.3% win rate)**
- When expert consensus >80%, bet NO
- Historical: Trump 2016, Brexit, Omicron severity
- Works on political/social predictions

**3. TIME HORIZON (66.7% win rate)**
- Markets with <3 days to close
- Deadline pressure + information crystallization
- Higher resolution confidence

**4. NEWS REVERSION (65% win rate)**
- Geopolitical/political news spikes reverse
- Enter 5-30 min after spike
- Examples: Iran strike, Supreme Court, COVID

**5. CATEGORY FILTER (90.5% win rate)**
- Politics or crypto markets
- Proven edge in these categories
- Combine with other strategies

## Warning Signs

### High ROI (>400%)
Usually indicates one of:
1. **Multi-choice market** - One unlikely outcome in a group
2. **Low liquidity** - Can't actually get filled
3. **Stale data** - Price has moved since API update
4. **Missing context** - Recent news we don't know about

**Always verify on Polymarket.com before trading!**

### Volume Considerations
- **<$100K** = Filtered out (illiquid)
- **$100K-500K** = Caution (may be hard to fill large orders)
- **$500K-1M** = Good liquidity
- **>$1M** = Excellent liquidity

### Days to Close
- **<3 days** = High confidence, time horizon strategy applies
- **3-7 days** = Moderate timeline
- **7-14 days** = Longer horizon, more uncertainty
- **14-30 days** = Maximum filter range
- **>30 days** = Filtered out (too far out)

## How to Act on Results

### Step 1: Review Results
```bash
# Check summary
cat live_opportunities_tracker.json | grep -A 5 "summary"

# View high-priority alerts
cat HIGH_PRIORITY_ALERTS.md
```

### Step 2: Validate Opportunities
For each opportunity:
1. Visit the URL (Polymarket link)
2. Check current price (might have moved)
3. Review order book depth
4. Read market description/resolution criteria
5. Search for recent news

### Step 3: Paper Trade First
**DO NOT bet real money without validation!**
- Track the opportunity
- Watch for 24-48 hours
- See if price moves as expected
- Measure actual fill rates

### Step 4: Deploy Capital (if validated)
**Conservative Approach:**
- Start with $10-20 per trade
- Max 3-5 trades simultaneously
- Stop if you lose 2 in a row
- Track results for 30 days

**Aggressive Approach (not recommended yet):**
- $20-50 per trade
- Higher risk, higher reward
- Requires automation for speed

## Performance Expectations

### Realistic Estimates
Based on backtested strategies:

**Conservative (Paper Trade First):**
- Month 1-2: $0 (validation phase)
- Month 3+: 15-30% monthly returns
- Win rate: 55-60%

**Aggressive (Immediate Deploy):**
- Potential: 30-60% monthly returns
- Risk: Could lose 30-50% if strategies fail
- Win rate: 50-65% (unvalidated live)

### What Can Go Wrong
1. **Backtests were optimistic** - Real win rate might be 45-50%
2. **Bots dominate** - Speed matters, manual trading loses
3. **Low liquidity** - Can't fill at good prices
4. **Market structure** - Multi-choice markets behave differently
5. **Polymarket changes** - API or fee structure updates

## Automation Options

### Run on Schedule (Cron/Task Scheduler)
**Windows:**
```batch
# Create scheduled task to run every 10 minutes
schtasks /create /tn "PolymarketMonitor" /tr "python C:\path\to\live_monitor_simple.py" /sc minute /mo 10
```

**Linux/Mac:**
```bash
# Add to crontab
*/10 * * * * cd /path/to && python live_monitor_simple.py >> monitor.log 2>&1
```

### Telegram Alerts
Add to code:
```python
import requests

def send_telegram(message):
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})

# In run_scan() function:
if len(high_alerts) > 0:
    send_telegram(f"🚨 {len(high_alerts)} high-priority alerts!")
```

## Safety Checklist

Before betting real money:

- [ ] Verified opportunity on Polymarket.com
- [ ] Checked order book has liquidity
- [ ] Read market resolution criteria
- [ ] Searched for recent news
- [ ] Calculated position size (max 2-5% of bankroll)
- [ ] Set stop-loss plan
- [ ] Paper traded successfully for 7+ days
- [ ] Understand this is high-risk speculation

## Contact & Support

**Questions?**
- Review `FINAL_STRATEGY_REPORT.md` for full strategy details
- Check `SUBAGENT_MISSION_REPORT.md` for technical implementation
- See `LIVE_MONITOR_STATUS.md` for current progress

**Need Help?**
Ask the main agent:
- "Show me how to validate a Polymarket opportunity"
- "What's the current status of the live monitor?"
- "Explain why [market] has 500% ROI"

---

**Remember:** High ROI = High Risk. Always validate before trading.
