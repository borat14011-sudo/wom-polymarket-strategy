"""
Real Backtest Analysis - Time-Based Patterns
Analyzes resolved Polymarket data for time-based trading edges
WITH REALISTIC COSTS: 4% roundtrip fees + 1.5% slippage = 5.5% total
"""

import json
from datetime import datetime, timezone
from collections import defaultdict
import statistics
import math

print("=" * 60)
print("REAL BACKTEST: TIME-BASED PATTERN ANALYSIS")
print("=" * 60)

# Load polymarket_complete.json which has outcome data
DATA_PATH = r"C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\polymarket_complete.json"
BACKTEST_PATH = r"C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json"

print("\nLoading polymarket_complete.json for outcomes...")
with open(DATA_PATH, 'r', encoding='utf-8') as f:
    events_data = json.load(f)

print("Loading backtest_dataset_v1.json for price histories...")
with open(BACKTEST_PATH, 'r', encoding='utf-8') as f:
    backtest_data = json.load(f)

# Create lookup for price histories by market_id
price_history_lookup = {}
for market in backtest_data:
    mid = str(market.get('market_id'))
    ph = market.get('price_history', [])
    if ph:
        price_history_lookup[mid] = {
            'price_history': ph,
            'end_date': market.get('end_date'),
            'question': market.get('question', '')
        }

print(f"Markets with price history: {len(price_history_lookup)}")

# Extract resolved markets with outcomes
resolved_markets = []
outcome_stats = {'yes_won': 0, 'no_won': 0, 'other': 0}

for event in events_data:
    if not event.get('closed'):
        continue
    
    for market in event.get('markets', []):
        market_id = str(market.get('market_id'))
        outcome_prices = market.get('outcome_prices', '')
        
        # Parse outcome
        try:
            prices = json.loads(outcome_prices)
            if prices == ['1', '0'] or prices == [1, 0]:
                yes_won = True
                outcome_stats['yes_won'] += 1
            elif prices == ['0', '1'] or prices == [0, 1]:
                yes_won = False
                outcome_stats['no_won'] += 1
            else:
                outcome_stats['other'] += 1
                continue
        except:
            continue
        
        # Find price history
        if market_id in price_history_lookup:
            ph_data = price_history_lookup[market_id]
            resolved_markets.append({
                'market_id': market_id,
                'question': market.get('question', ph_data.get('question', '')),
                'yes_won': yes_won,
                'price_history': ph_data['price_history'],
                'end_date': ph_data['end_date'],
                'volume': event.get('volume', 0)
            })

print(f"\nOutcome Statistics:")
print(f"  YES won: {outcome_stats['yes_won']:,}")
print(f"  NO won: {outcome_stats['no_won']:,}")
print(f"  Other: {outcome_stats['other']:,}")
print(f"\nResolved markets with price history: {len(resolved_markets)}")

# Trading costs
ROUNDTRIP_FEE = 0.04  # 4%
SLIPPAGE = 0.015      # 1.5%
TOTAL_COSTS = ROUNDTRIP_FEE + SLIPPAGE  # 5.5%

print(f"\n=== COSTS APPLIED ===")
print(f"Roundtrip fees: {ROUNDTRIP_FEE*100:.1f}%")
print(f"Slippage: {SLIPPAGE*100:.1f}%")
print(f"Total costs per trade: {TOTAL_COSTS*100:.1f}%")

# Analysis storage
time_of_day = defaultdict(lambda: {'returns': [], 'wins': 0, 'losses': 0})
day_of_week = defaultdict(lambda: {'returns': [], 'wins': 0, 'losses': 0})
days_to_close = defaultdict(lambda: {'returns': [], 'wins': 0, 'losses': 0})
price_buckets = defaultdict(lambda: {'returns': [], 'wins': 0, 'losses': 0})
buy_yes = {'returns': [], 'wins': 0, 'losses': 0}
buy_no = {'returns': [], 'wins': 0, 'losses': 0}
buy_cheap = {'returns': [], 'wins': 0, 'losses': 0, 'trades': []}

total_trades = 0

for market in resolved_markets:
    yes_won = market['yes_won']
    price_history = market['price_history']
    
    if len(price_history) < 5:
        continue
    
    # Parse end_date
    try:
        end_str = market.get('end_date', '')
        if end_str:
            end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        else:
            continue
    except:
        continue
    
    for point in price_history:
        timestamp = point.get('t')
        price = point.get('p')
        
        if timestamp is None or price is None:
            continue
        
        # Skip extreme prices
        if price < 0.03 or price > 0.97:
            continue
        
        try:
            entry_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except:
            continue
        
        hour = entry_time.hour
        dow = entry_time.weekday()
        
        try:
            days_remaining = (end_date - entry_time).total_seconds() / 86400
        except:
            days_remaining = -1
        
        # Calculate returns for buying YES at this price
        if yes_won:
            gross_return = (1.0 - price) / price
            net_return = gross_return - TOTAL_COSTS
        else:
            # YES lost, we lose our stake
            net_return = -1.0 - TOTAL_COSTS
        
        win = net_return > 0
        
        # Record for overall buy YES strategy
        buy_yes['returns'].append(net_return)
        if win:
            buy_yes['wins'] += 1
        else:
            buy_yes['losses'] += 1
        
        # Time of day
        time_of_day[hour]['returns'].append(net_return)
        if win:
            time_of_day[hour]['wins'] += 1
        else:
            time_of_day[hour]['losses'] += 1
        
        # Day of week
        day_of_week[dow]['returns'].append(net_return)
        if win:
            day_of_week[dow]['wins'] += 1
        else:
            day_of_week[dow]['losses'] += 1
        
        # Days to close
        if 0 <= days_remaining <= 30:
            bucket = int(days_remaining)
            days_to_close[bucket]['returns'].append(net_return)
            if win:
                days_to_close[bucket]['wins'] += 1
            else:
                days_to_close[bucket]['losses'] += 1
        
        # Price bucket analysis (for buying YES)
        price_bucket = int(price * 10) / 10  # 0.1, 0.2, etc.
        price_buckets[price_bucket]['returns'].append(net_return)
        if win:
            price_buckets[price_bucket]['wins'] += 1
        else:
            price_buckets[price_bucket]['losses'] += 1
        
        # Buy cheap strategy: buy YES when price < 0.20
        if price < 0.20 and yes_won:
            buy_cheap['returns'].append(net_return)
            buy_cheap['wins'] += 1
            buy_cheap['trades'].append({
                'price': price,
                'return': net_return,
                'market': market['question'][:50]
            })
        elif price < 0.20 and not yes_won:
            buy_cheap['returns'].append(net_return)
            buy_cheap['losses'] += 1
        
        total_trades += 1

print(f"\n{'='*60}")
print(f"TOTAL TRADE OPPORTUNITIES ANALYZED: {total_trades:,}")
print(f"{'='*60}")

# Helper function for statistical significance
def calc_stats(returns):
    if len(returns) < 30:
        return None
    mean = statistics.mean(returns)
    stdev = statistics.stdev(returns)
    if stdev == 0:
        return None
    stderr = stdev / math.sqrt(len(returns))
    t_stat = mean / stderr
    return {
        'mean': mean,
        'stdev': stdev,
        't_stat': t_stat,
        'n': len(returns)
    }

# Print results
print("\n" + "=" * 60)
print("TIME OF DAY ANALYSIS (Hours in UTC)")
print("=" * 60)
print(f"{'Hour':>4} | {'Trades':>8} | {'Win Rate':>8} | {'Avg Return':>10} | {'T-stat':>8} | Sig")
print("-" * 60)

significant_hours = []
for hour in sorted(time_of_day.keys()):
    data = time_of_day[hour]
    n = len(data['returns'])
    if n < 100:
        continue
    win_rate = data['wins'] / n * 100
    avg_ret = statistics.mean(data['returns']) * 100
    
    stats = calc_stats(data['returns'])
    t_stat = stats['t_stat'] if stats else 0
    sig = "***" if abs(t_stat) > 2.58 else "**" if abs(t_stat) > 1.96 else "*" if abs(t_stat) > 1.64 else ""
    
    if t_stat > 1.96:
        significant_hours.append((hour, avg_ret, t_stat, n))
    
    print(f"{hour:4} | {n:8,} | {win_rate:7.1f}% | {avg_ret:+9.2f}% | {t_stat:+8.2f} | {sig}")

print("\n" + "=" * 60)
print("DAY OF WEEK ANALYSIS")
print("=" * 60)
dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
print(f"{'Day':>4} | {'Trades':>8} | {'Win Rate':>8} | {'Avg Return':>10} | {'T-stat':>8} | Sig")
print("-" * 60)

significant_days = []
for dow in sorted(day_of_week.keys()):
    data = day_of_week[dow]
    n = len(data['returns'])
    if n < 100:
        continue
    win_rate = data['wins'] / n * 100
    avg_ret = statistics.mean(data['returns']) * 100
    
    stats = calc_stats(data['returns'])
    t_stat = stats['t_stat'] if stats else 0
    sig = "***" if abs(t_stat) > 2.58 else "**" if abs(t_stat) > 1.96 else "*" if abs(t_stat) > 1.64 else ""
    
    if t_stat > 1.96:
        significant_days.append((dow_names[dow], avg_ret, t_stat, n))
    
    print(f"{dow_names[dow]:>4} | {n:8,} | {win_rate:7.1f}% | {avg_ret:+9.2f}% | {t_stat:+8.2f} | {sig}")

print("\n" + "=" * 60)
print("DAYS TO RESOLUTION ANALYSIS")
print("=" * 60)
print(f"{'Days':>4} | {'Trades':>8} | {'Win Rate':>8} | {'Avg Return':>10} | {'T-stat':>8} | Sig")
print("-" * 60)

significant_days_to_close = []
for days in sorted(days_to_close.keys()):
    data = days_to_close[days]
    n = len(data['returns'])
    if n < 50:
        continue
    win_rate = data['wins'] / n * 100
    avg_ret = statistics.mean(data['returns']) * 100
    
    stats = calc_stats(data['returns'])
    t_stat = stats['t_stat'] if stats else 0
    sig = "***" if abs(t_stat) > 2.58 else "**" if abs(t_stat) > 1.96 else "*" if abs(t_stat) > 1.64 else ""
    
    if t_stat > 1.96:
        significant_days_to_close.append((days, avg_ret, t_stat, n))
    
    print(f"{days:4} | {n:8,} | {win_rate:7.1f}% | {avg_ret:+9.2f}% | {t_stat:+8.2f} | {sig}")

print("\n" + "=" * 60)
print("ENTRY PRICE ANALYSIS (Buy YES at price X)")
print("=" * 60)
print(f"{'Price':>6} | {'Trades':>8} | {'Win Rate':>8} | {'Avg Return':>10} | {'T-stat':>8} | Sig")
print("-" * 60)

positive_ev_buckets = []
for price in sorted(price_buckets.keys()):
    data = price_buckets[price]
    n = len(data['returns'])
    if n < 100:
        continue
    win_rate = data['wins'] / n * 100
    avg_ret = statistics.mean(data['returns']) * 100
    
    stats = calc_stats(data['returns'])
    t_stat = stats['t_stat'] if stats else 0
    sig = "***" if abs(t_stat) > 2.58 else "**" if abs(t_stat) > 1.96 else "*" if abs(t_stat) > 1.64 else ""
    
    if avg_ret > 0 and t_stat > 1.96:
        positive_ev_buckets.append((price, avg_ret, t_stat, n))
    
    print(f"{price:6.1f} | {n:8,} | {win_rate:7.1f}% | {avg_ret:+9.2f}% | {t_stat:+8.2f} | {sig}")

print("\n" + "=" * 60)
print("OVERALL STRATEGY RESULTS (with 5.5% costs)")
print("=" * 60)

print("\n--- Buy YES (all trades) ---")
n = len(buy_yes['returns'])
if n > 0:
    win_rate = buy_yes['wins'] / n * 100
    avg_ret = statistics.mean(buy_yes['returns']) * 100
    stats = calc_stats(buy_yes['returns'])
    print(f"  Trades: {n:,}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Average Net Return: {avg_ret:+.2f}%")
    if stats:
        print(f"  T-statistic: {stats['t_stat']:+.2f}")

print("\n--- Buy Cheap (<20%) Strategy ---")
n = len(buy_cheap['returns'])
if n > 0:
    win_rate = buy_cheap['wins'] / n * 100
    avg_ret = statistics.mean(buy_cheap['returns']) * 100
    stats = calc_stats(buy_cheap['returns'])
    print(f"  Trades: {n:,}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Average Net Return: {avg_ret:+.2f}%")
    if stats:
        print(f"  T-statistic: {stats['t_stat']:+.2f}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY: STRATEGIES WITH POSITIVE EDGE (p < 0.05)")
print("=" * 60)

print("\n📊 Statistically Significant Time of Day Effects:")
if significant_hours:
    for hour, ret, t, n in significant_hours:
        print(f"  Hour {hour:02d} UTC: +{ret:.2f}% avg return (t={t:.2f}, n={n:,})")
else:
    print("  None found")

print("\n📊 Statistically Significant Day of Week Effects:")
if significant_days:
    for day, ret, t, n in significant_days:
        print(f"  {day}: +{ret:.2f}% avg return (t={t:.2f}, n={n:,})")
else:
    print("  None found")

print("\n📊 Statistically Significant Days-to-Close Effects:")
if significant_days_to_close:
    for days, ret, t, n in significant_days_to_close:
        print(f"  {days} days before: +{ret:.2f}% avg return (t={t:.2f}, n={n:,})")
else:
    print("  None found")

print("\n📊 Price Buckets with Positive EV (p < 0.05):")
if positive_ev_buckets:
    for price, ret, t, n in positive_ev_buckets:
        print(f"  Buy at {price:.1f}: +{ret:.2f}% avg return (t={t:.2f}, n={n:,})")
else:
    print("  None found")
