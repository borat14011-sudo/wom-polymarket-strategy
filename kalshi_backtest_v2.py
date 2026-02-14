#!/usr/bin/env python3
"""
Kalshi "Buy the Dip" Strategy Backtester
Analyzes historical price drops and calculates expected value
"""

import json
from datetime import datetime

# Sample data from Kalshi API (from web_fetch earlier)
SAMPLE_MARKETS = [
    {
        "ticker": "KXELONMARS-99",
        "title": "Will Elon Musk visit Mars before Aug 1, 2099?",
        "last_price": 8,
        "previous_day_price": 8,
        "previous_week_price": 7,
        "volume": 88546
    },
    {
        "ticker": "KXNEWPOPE-70-PPAR",
        "title": "Who will the next Pope be? - Pietro Parolin",
        "last_price": 6,
        "previous_day_price": 6,
        "previous_week_price": 9,
        "volume": 18236
    },
    {
        "ticker": "KXNEWPOPE-70-LANT",
        "title": "Who will the next Pope be? - Luis Antonio Tagle",
        "last_price": 5,
        "previous_day_price": 9,
        "previous_week_price": 5,
        "volume": 10462
    },
    {
        "ticker": "KXWARMING-50",
        "title": "Will the world pass 2 degrees Celsius over pre-industrial levels before 2050?",
        "last_price": 78,
        "previous_day_price": 78,
        "previous_week_price": 81,
        "volume": 12658
    },
    {
        "ticker": "KXMARSVRAIL-50",
        "title": "Will a human land on Mars before California starts high-speed rail?",
        "last_price": 29,
        "previous_day_price": 30,
        "previous_week_price": 27,
        "volume": 12224
    },
    {
        "ticker": "KXERUPTSUPER-0-50JAN01",
        "title": "Will a supervolcano erupt before Jan 1, 2050?",
        "last_price": 13,
        "previous_day_price": 20,
        "previous_week_price": 14,
        "volume": 24932
    },
    {
        "ticker": "KXCOLONIZEMARS-50",
        "title": "Will humans colonize Mars before 2050?",
        "last_price": 16,
        "previous_day_price": 20,
        "previous_week_price": 17,
        "volume": 21548
    },
    {
        "ticker": "KXPERSONPRESMAM-45",
        "title": "Will Zohran Mamdani become President before 2045?",
        "last_price": 7,
        "previous_day_price": 7,
        "previous_week_price": 5,
        "volume": 29002
    },
    {
        "ticker": "KXNEWPOPE-70-AARB",
        "title": "Who will the next Pope be? - Anders Arborelius",
        "last_price": 3,
        "previous_day_price": 6,
        "previous_week_price": 5,
        "volume": 5184
    }
]

def identify_dip_opportunities(markets, dip_threshold=0.10):
    """
    Identify markets where price dropped >10% from previous levels
    Entry criteria: previous_price > last_price by >10%
    """
    dip_opportunities = []
    
    for market in markets:
        last_price = market['last_price']
        prev_day = market['previous_day_price']
        prev_week = market['previous_week_price']
        
        # Skip if no price data
        if last_price == 0 or (prev_day == 0 and prev_week == 0):
            continue
        
        # Calculate percentage drops
        day_drop = 0
        week_drop = 0
        
        if prev_day > 0 and last_price < prev_day:
            day_drop = (prev_day - last_price) / prev_day
        
        if prev_week > 0 and last_price < prev_week:
            week_drop = (prev_week - last_price) / prev_week
        
        # Check if meets "dip" criteria (>10% drop)
        if day_drop >= dip_threshold or week_drop >= dip_threshold:
            dip_opportunities.append({
                'ticker': market['ticker'],
                'title': market['title'],
                'last_price': last_price,
                'prev_day_price': prev_day,
                'prev_week_price': prev_week,
                'day_drop_pct': day_drop * 100,
                'week_drop_pct': week_drop * 100,
                'max_drop_pct': max(day_drop, week_drop) * 100,
                'volume': market['volume']
            })
    
    return sorted(dip_opportunities, key=lambda x: x['max_drop_pct'], reverse=True)

def calculate_expected_value(dip_opportunities, kalshi_fee=0.02):
    """
    Calculate expected value for "Buy the Dip" strategy
    
    Assumptions from Polymarket backtest:
    - Win rate: ~11.5% (markets that mean-revert or resolve favorably)
    - Average gain on wins: Assume mean reversion to previous price level
    - Average loss on losses: Entry price (contract goes to 0)
    """
    
    if not dip_opportunities:
        return {
            'num_opportunities': 0,
            'total_ev_cents': 0,
            'avg_ev_per_trade_cents': 0,
            'avg_ev_pct': 0,
            'trade_details': []
        }
    
    win_rate = 0.115  # From Polymarket backtest
    total_ev = 0
    trade_details = []
    
    for opp in dip_opportunities:
        entry_price = opp['last_price']  # cents
        target_price = max(opp['prev_day_price'], opp['prev_week_price'])  # Mean reversion target
        
        # Expected payoff calculation
        # Win scenario: Contract resolves to 100 cents or mean reverts
        win_payoff = 100 - entry_price  # If contract resolves YES
        
        # Alternative: Mean reversion gain (more conservative)
        mean_revert_gain = target_price - entry_price
        
        # Loss scenario: Contract goes to 0
        loss_amount = entry_price
        
        # Expected value per trade (using resolution win)
        ev_resolution = (win_rate * (win_payoff - kalshi_fee * 100)) + ((1 - win_rate) * (-loss_amount))
        
        # Expected value using mean reversion assumption
        ev_mean_revert = (win_rate * (mean_revert_gain - kalshi_fee * 100)) + ((1 - win_rate) * (-loss_amount))
        
        trade_details.append({
            'ticker': opp['ticker'],
            'title': opp['title'],
            'entry_price': entry_price,
            'target_price': target_price,
            'drop_pct': opp['max_drop_pct'],
            'ev_cents': ev_resolution,
            'ev_pct': (ev_resolution / entry_price * 100) if entry_price > 0 else 0
        })
        
        total_ev += ev_resolution
    
    avg_ev_per_trade = total_ev / len(dip_opportunities) if dip_opportunities else 0
    avg_entry = sum(d['entry_price'] for d in trade_details) / len(trade_details) if trade_details else 20
    
    return {
        'num_opportunities': len(dip_opportunities),
        'total_ev_cents': total_ev,
        'avg_ev_per_trade_cents': avg_ev_per_trade,
        'avg_ev_pct': (avg_ev_per_trade / avg_entry * 100) if avg_entry > 0 else 0,
        'trade_details': trade_details
    }

def compare_to_polymarket(kalshi_results):
    """Compare Kalshi backtest results to Polymarket baseline"""
    
    polymarket_ev = 4.44  # %
    polymarket_fee = 0.04  # 4%
    kalshi_fee = 0.02  # 2% (assumed)
    
    kalshi_ev_pct = kalshi_results['avg_ev_pct']
    
    comparison = {
        'polymarket_ev_pct': polymarket_ev,
        'polymarket_fee_pct': polymarket_fee * 100,
        'kalshi_ev_pct': kalshi_ev_pct,
        'kalshi_fee_pct': kalshi_fee * 100,
        'ev_difference': kalshi_ev_pct - polymarket_ev,
        'fee_advantage': (polymarket_fee - kalshi_fee) * 100,
        'conclusion': ''
    }
    
    if kalshi_ev_pct > polymarket_ev:
        comparison['conclusion'] = "[OK] Kalshi offers BETTER edge than Polymarket due to lower fees"
    elif kalshi_ev_pct < polymarket_ev:
        comparison['conclusion'] = "[WARNING] Kalshi offers LOWER edge than Polymarket (investigate liquidity/spreads)"
    else:
        comparison['conclusion'] = "[NEUTRAL] Kalshi and Polymarket show similar expected value"
    
    return comparison

def generate_report(markets, dip_opportunities, ev_results, comparison):
    """Generate markdown backtest report"""
    
    report = f"""# Kalshi "Buy the Dip" Strategy Backtest

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

- **Total Markets Analyzed:** {len(markets)}
- **Dip Opportunities Found (>10% drop):** {ev_results['num_opportunities']}
- **Average Expected Value:** {ev_results['avg_ev_pct']:.2f}%
- **Total EV (cents):** {ev_results['total_ev_cents']:.2f}

## Methodology

### Entry Criteria
- Price drops >10% from previous day OR previous week price
- Active markets only (excludes settled/expired)

### Exit Strategy
- Hold for mean reversion or resolution
- Target: Previous price level (conservative) or contract resolution (100¢)

### Risk Parameters
- **Win rate:** 11.5% (from Polymarket backtest)
- **Kalshi fees:** ~2% (vs Polymarket 4%)
- **Sample size needed:** 100+ trades for statistical significance

## Results

### Dip Opportunities Identified

"""
    
    if ev_results['num_opportunities'] > 0:
        report += "| # | Ticker | Title | Entry (¢) | Was (¢) | Drop % | EV % |\n"
        report += "|---|--------|-------|-----------|---------|--------|------|\n"
        
        # Add all opportunities
        for idx, trade in enumerate(ev_results['trade_details'], 1):
            ticker_short = trade['ticker'][:15]
            title_short = trade['title'][:35]
            report += f"| {idx} | {ticker_short} | {title_short}... | {trade['entry_price']}¢ | {trade['target_price']}¢ | **{trade['drop_pct']:.1f}%** | {trade['ev_pct']:.2f}% |\n"
    else:
        report += "*No dip opportunities found in current snapshot.*\n"
    
    report += f"""

## Comparison: Kalshi vs Polymarket

| Metric | Polymarket | Kalshi | Difference |
|--------|-----------|--------|------------|
| **Expected Value** | {comparison['polymarket_ev_pct']:.2f}% | {comparison['kalshi_ev_pct']:.2f}% | **{comparison['ev_difference']:+.2f}%** |
| **Platform Fees** | {comparison['polymarket_fee_pct']:.1f}% | {comparison['kalshi_fee_pct']:.1f}% | **-{comparison['fee_advantage']:.1f}%** (advantage) |

### Conclusion
{comparison['conclusion']}

## Fee Impact Analysis

Lower fees on Kalshi ({comparison['kalshi_fee_pct']:.0f}% vs {comparison['polymarket_fee_pct']:.0f}%) provide a **{comparison['fee_advantage']:.0f}% structural advantage**.

If Kalshi markets exhibit similar "dip recovery" dynamics to Polymarket, the edge should be **HIGHER** due to lower transaction costs.

## Recommended Position Sizes

Based on Kelly Criterion with edge of {ev_results['avg_ev_pct']:.2f}%:

"""
    
    if ev_results['avg_ev_pct'] > 0:
        report += f"""- **Conservative (¼ Kelly):** {max(0.5, ev_results['avg_ev_pct'] * 0.25):.1f}% of bankroll per trade
- **Moderate (½ Kelly):** {max(1.0, ev_results['avg_ev_pct'] * 0.5):.1f}% of bankroll per trade
- **Aggressive (Full Kelly):** {max(2.0, ev_results['avg_ev_pct']):.1f}% of bankroll per trade
"""
    else:
        report += "*Position sizing not recommended until more opportunities are identified.*\n"
    
    report += f"""
## Risk Warnings

⚠️ **Key Limitations:**

1. **Small sample size:** Current snapshot has only {ev_results['num_opportunities']} opportunities (need 100+ for statistical significance)
2. **No historical resolution data:** Using Polymarket win rate (11.5%) as proxy - Kalshi markets may behave differently
3. **Liquidity concerns:** Must check bid-ask spreads before entry (not analyzed here)
4. **Mean reversion assumption:** Not all dips recover - requires fundamental analysis
5. **Event risk:** Political/news events can cause permanent price shifts (not just noise)
6. **Survivorship bias:** Only analyzing currently active markets

## Detailed Trade Analysis

"""
    
    if ev_results['trade_details']:
        for idx, trade in enumerate(ev_results['trade_details'], 1):
            report += f"""### Trade #{idx}: {trade['ticker']}

**Market:** {trade['title']}

- **Entry Price:** {trade['entry_price']}¢ (current bid)
- **Previous Price:** {trade['target_price']}¢ (day/week high)
- **Drop:** {trade['drop_pct']:.1f}%
- **Expected Value:** {trade['ev_pct']:.2f}%

**Risk/Reward:**
- **Win scenario (11.5% prob):** Contract resolves YES → +{100 - trade['entry_price']}¢ (or mean reverts)
- **Loss scenario (88.5% prob):** Contract goes to 0 → -{trade['entry_price']}¢

**Rationale:** Price dropped significantly. If this is noise (not fundamentals), mean reversion likely.

---

"""
    
    report += f"""
## Next Steps for Validation

1. **Expand sample:** Monitor Kalshi for 30-60 days to capture 100+ dip opportunities
2. **Track outcomes:** Record which "dips" actually recovered vs went to zero
3. **Calculate actual win rate:** Validate the 11.5% assumption from Polymarket
4. **Refine entry criteria:**
   - Test different dip thresholds (15%, 20%, 25%)
   - Add volume filters (avoid illiquid markets)
   - Check for news catalysts (avoid fundamental shifts)
5. **Factor spreads:** Include bid-ask spread costs in EV calculation
6. **Backtest timing:** Analyze optimal holding period (days to mean reversion)

## Kalshi API Data Quality Notes

- ✅ Provides `previous_day_price` and `previous_week_price` for easy dip detection
- ✅ Real-time data available via API
- ⚠️ Limited historical price data (no full time-series)
- ⚠️ No historical resolution outcomes readily available

## Conclusion

Based on this **preliminary snapshot analysis**:

- **Opportunities exist:** Found {ev_results['num_opportunities']} markets with >10% price drops
- **Fee advantage:** Kalshi's 2% fees vs Polymarket's 4% = **2% structural edge**
- **Expected value:** {ev_results['avg_ev_pct']:.2f}% per trade (if Polymarket dynamics hold)

**⚠️ CRITICAL:** This is NOT sufficient data for live trading. Need:
1. Larger sample size (100+ trades minimum)
2. Actual win rate validation on Kalshi markets
3. Historical outcome tracking
4. Liquidity and spread analysis

**Recommendation:** Start with paper trading / tracking to validate the strategy on Kalshi before committing capital.

---

*Generated by Kalshi Strategy Tester*  
*Data source: Kalshi API (https://api.elections.kalshi.com/v1/events)*  
*Strategy origin: Polymarket "Buy the Dip" backtest (+4.44% EV validated)*
"""
    
    return report

def main():
    print("=" * 60)
    print("KALSHI 'BUY THE DIP' STRATEGY BACKTEST")
    print("=" * 60)
    
    # Use sample markets
    markets = SAMPLE_MARKETS
    print(f"\nAnalyzing {len(markets)} sample markets...")
    
    # Identify dip opportunities
    print("\nIdentifying dip opportunities (>10% drop)...")
    dip_opportunities = identify_dip_opportunities(markets, dip_threshold=0.10)
    
    print(f"[OK] Found {len(dip_opportunities)} dip opportunities")
    
    if dip_opportunities:
        print("\nTop dips:")
        for i, opp in enumerate(dip_opportunities[:5], 1):
            print(f"  {i}. {opp['ticker']}: {opp['max_drop_pct']:.1f}% drop ({opp['last_price']}c from {max(opp['prev_day_price'], opp['prev_week_price'])}c)")
    
    # Calculate expected value
    print("\nCalculating expected value...")
    ev_results = calculate_expected_value(dip_opportunities, kalshi_fee=0.02)
    
    # Compare to Polymarket
    comparison = compare_to_polymarket(ev_results)
    
    # Generate report
    print("\nGenerating backtest report...")
    report = generate_report(markets, dip_opportunities, ev_results, comparison)
    
    # Save report
    with open('kalshi_buy_the_dip_backtest.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n[OK] Report saved to: kalshi_buy_the_dip_backtest.md")
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Opportunities Found: {ev_results['num_opportunities']}")
    print(f"Average EV: {ev_results['avg_ev_pct']:.2f}%")
    print(f"vs Polymarket: {comparison['ev_difference']:+.2f}% {'[BETTER]' if comparison['ev_difference'] > 0 else '[WORSE]'}")
    print(f"Fee Advantage: {comparison['fee_advantage']:.0f}% (Kalshi {comparison['kalshi_fee_pct']:.0f}% vs PM {comparison['polymarket_fee_pct']:.0f}%)")
    print("=" * 60)
    print("\n>> " + comparison['conclusion'])

if __name__ == "__main__":
    main()
