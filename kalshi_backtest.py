#!/usr/bin/env python3
"""
Kalshi "Buy the Dip" Strategy Backtester
Analyzes historical price drops and calculates expected value
"""

import json
import requests
from datetime import datetime

# Fetch Kalshi market data
API_URL = "https://api.elections.kalshi.com/v1/events"

def fetch_kalshi_markets():
    """Fetch all active Kalshi markets"""
    print("Fetching Kalshi market data...")
    response = requests.get(f"{API_URL}?limit=200&status=active")
    data = response.json()
    
    markets = []
    for event in data.get('events', []):
        for market in event.get('markets', []):
            markets.append({
                'ticker': market.get('ticker_name'),
                'title': market.get('title', ''),
                'last_price': market.get('last_price', 0),
                'prev_period_price': market.get('prev_period_price', 0),
                'previous_hour_price': market.get('previous_hour_price', 0),
                'previous_day_price': market.get('previous_day_price', 0),
                'previous_week_price': market.get('previous_week_price', 0),
                'volume': market.get('volume', 0),
                'open_interest': market.get('open_interest', 0),
                'yes_bid': market.get('yes_bid', 0),
                'yes_ask': market.get('yes_ask', 0),
                'status': market.get('status', '')
            })
    
    print(f"Fetched {len(markets)} markets")
    return markets

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
                'volume': market['volume'],
                'spread': market['yes_ask'] - market['yes_bid']
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
        return None
    
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
            'entry_price': entry_price,
            'target_price': target_price,
            'drop_pct': opp['max_drop_pct'],
            'ev_cents': ev_resolution,
            'ev_pct': (ev_resolution / entry_price * 100) if entry_price > 0 else 0
        })
        
        total_ev += ev_resolution
    
    avg_ev_per_trade = total_ev / len(dip_opportunities) if dip_opportunities else 0
    
    return {
        'num_opportunities': len(dip_opportunities),
        'total_ev_cents': total_ev,
        'avg_ev_per_trade_cents': avg_ev_per_trade,
        'avg_ev_pct': (avg_ev_per_trade / 20) * 100,  # Assuming avg entry ~20 cents
        'trade_details': trade_details[:10]  # Top 10 trades
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
        comparison['conclusion'] = "Kalshi offers BETTER edge than Polymarket due to lower fees"
    elif kalshi_ev_pct < polymarket_ev:
        comparison['conclusion'] = "Kalshi offers LOWER edge than Polymarket (investigate liquidity/spreads)"
    else:
        comparison['conclusion'] = "Kalshi and Polymarket show similar expected value"
    
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
- Win rate: 11.5% (from Polymarket backtest)
- Kalshi fees: ~2% (vs Polymarket 4%)
- Sample size needed: 100+ trades for statistical significance

## Results

### Dip Opportunities Identified

| Ticker | Title | Entry Price | Drop % | EV % |
|--------|-------|-------------|--------|------|
"""
    
    # Add top opportunities
    for trade in ev_results['trade_details'][:10]:
        report += f"| {trade['ticker'][:20]} | {trade['ticker'][:30]}... | {trade['entry_price']}¢ | {trade['drop_pct']:.1f}% | {trade['ev_pct']:.2f}% |\n"
    
    report += f"""

## Comparison: Kalshi vs Polymarket

| Metric | Polymarket | Kalshi | Difference |
|--------|-----------|--------|------------|
| Expected Value | {comparison['polymarket_ev_pct']:.2f}% | {comparison['kalshi_ev_pct']:.2f}% | {comparison['ev_difference']:.2f}% |
| Platform Fees | {comparison['polymarket_fee_pct']:.1f}% | {comparison['kalshi_fee_pct']:.1f}% | -{comparison['fee_advantage']:.1f}% |

### Conclusion
{comparison['conclusion']}

## Recommended Position Sizes

Based on Kelly Criterion with edge of {ev_results['avg_ev_pct']:.2f}%:

- **Conservative (¼ Kelly):** {max(0.5, ev_results['avg_ev_pct'] * 0.25):.1f}% of bankroll per trade
- **Moderate (½ Kelly):** {max(1.0, ev_results['avg_ev_pct'] * 0.5):.1f}% of bankroll per trade
- **Aggressive (Full Kelly):** {max(2.0, ev_results['avg_ev_pct']):.1f}% of bankroll per trade

## Risk Warnings

⚠️ **Key Limitations:**
1. **Sample size:** Current snapshot has {ev_results['num_opportunities']} opportunities (need 100+ for significance)
2. **No historical resolution data:** Using Polymarket win rate (11.5%) as proxy
3. **Liquidity concerns:** Check bid-ask spreads before entry
4. **Mean reversion assumption:** Not all dips recover
5. **Event risk:** Political/news events can cause permanent price shifts

## Next Steps

1. **Collect more data:** Monitor for 30+ days to build larger sample
2. **Track actual outcomes:** Record which "dips" actually recovered
3. **Refine entry criteria:** Test different dip thresholds (15%, 20%)
4. **Monitor spreads:** Factor in bid-ask spread costs
5. **Validate win rate:** Kalshi markets may differ from Polymarket dynamics

---

*This is a preliminary backtest based on current market snapshot. Results should be validated with larger sample size and actual trading outcomes.*
"""
    
    return report

def main():
    print("=" * 60)
    print("KALSHI 'BUY THE DIP' STRATEGY BACKTEST")
    print("=" * 60)
    
    # Fetch markets
    markets = fetch_kalshi_markets()
    
    # Identify dip opportunities
    print("\nIdentifying dip opportunities (>10% drop)...")
    dip_opportunities = identify_dip_opportunities(markets, dip_threshold=0.10)
    
    print(f"Found {len(dip_opportunities)} dip opportunities")
    
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
    
    print("\n✅ Report saved to: kalshi_buy_the_dip_backtest.md")
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Opportunities Found: {ev_results['num_opportunities']}")
    print(f"Average EV: {ev_results['avg_ev_pct']:.2f}%")
    print(f"vs Polymarket: {comparison['ev_difference']:.2f}% {'better' if comparison['ev_difference'] > 0 else 'worse'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
