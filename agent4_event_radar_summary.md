# Event Radar Agent 4 - Summary Report

**Agent ID:** agent4  
**Market Range:** 60-79 (20 markets)  
**Analysis Timestamp:** 2026-02-07T22:45:42.853703Z

## Deliverables

✅ **Primary Output:** `agent4_event_radar.json`  
✅ **Analysis Script:** `agent4_event_radar_analyzer.py`  
✅ **Summary Report:** `agent4_event_radar_summary.md` (this file)

## Analysis Overview

Analyzed **20 markets** (indices 60-79) from the event radar inputs dataset, extracting historical patterns and event-driven signals.

## Key Findings

### Category Distribution
- **Crypto Markets:** 7 (35%)
- **Sports Props:** 6 (30%)
- **Esports:** 5 (25%)
- **Weather:** 1 (5%)
- **Stocks:** 1 (5%)

### Market Characteristics

**Volatility Analysis:**
- Average Volatility: **0.498** (49.8% price range)
- Max Volatility: **0.9995** (near-complete price swing)
- Min Volatility: **0.0065** (very stable)
- High Volatility Markets (>50%): **9 markets**

**Temporal Patterns:**
- Average Duration: **96.44 hours** (~4 days)
- Max Duration: **173.44 hours** (~7.2 days)
- Min Duration: **20.89 hours** (~0.87 days)
- Short-Duration Markets (<24h): **3 markets**

**Volume Insights:**
- Average Volume: **1,590,604.66**
- Total Volume: **31,812,093.13**
- High-Volume Markets (>$1M): **11 markets**

### Event Radar Signals Summary

Detected across 20 markets:
- **High Urgency:** 7 markets (35%) - primarily crypto micro-timeframe trades
- **Time Sensitive:** 7 markets (35%) - "Up or Down" style markets
- **Short Duration:** 5 markets (25%) - esports events
- **High Volatility:** 9 markets (45%) - wide price swings
- **Predictable Outcome:** 1 market (5%) - very low volatility

## Market Pattern Insights

### Crypto Markets (7 markets)
- **Dominant Signal:** Time-sensitive micro-timeframe trades
- **Pattern:** Bitcoin/XRP "Up or Down" markets with 15-minute windows
- **Characteristics:** Medium volatility (0.49-0.51), short duration (20-160h)

### Esports Markets (5 markets)
- **Dominant Signal:** Short-duration events
- **Pattern:** "Total Kills Over/Under" and team matchups
- **Characteristics:** Variable volatility, event-specific timing

### Sports Props Markets (6 markets)
- **Dominant Signal:** Player performance metrics
- **Pattern:** Points/Rebounds/Assists Over/Under
- **Characteristics:** High volume, medium-high volatility

### Notable Markets

**Highest Volume:**
- Market #62: Immanuel Quickley Rebounds O/U - **$4.52M volume**
- Market #79: Draymond Green Assists O/U - **$5.68M volume**

**Most Volatile:**
- Multiple markets with 0.99+ volatility (near-complete price swings)

**Time-Sensitive Crypto Trades:**
- 7 Bitcoin/crypto "Up or Down" markets
- Average duration: 22-160 hours
- Micro-timeframe event type

## Methodology

1. **Data Extraction:** Loaded markets 60-79 from event_radar_inputs.json
2. **Categorization:** Auto-classified markets by title keywords
3. **Signal Detection:** Identified event radar signals (urgency, volatility, timing)
4. **Aggregation:** Calculated distribution, volatility, temporal, and volume metrics
5. **Output:** Generated structured JSON with market patterns and insights

## Files Generated

```
agent4_event_radar.json          (9.3 KB) - Complete analysis data
agent4_event_radar_analyzer.py   (9.3 KB) - Analysis script
agent4_event_radar_summary.md    (This file) - Summary report
```

## Conclusion

Agent 4 successfully analyzed markets 60-79, identifying **7 crypto markets**, **6 sports props**, and **5 esports markets**. The subset shows **medium-high volatility** (avg 49.8%), **moderate duration** (avg 4 days), and **strong volume** ($31.8M total). Time-sensitive crypto trades and player performance props dominate the pattern landscape.

**Status:** ✅ COMPLETE  
**Next:** Integration with agents 1-3, 5 for comprehensive event radar synthesis
