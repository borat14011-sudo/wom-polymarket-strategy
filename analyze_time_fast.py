"""
Fast Backtest Analysis - Optimized for large files
"""

import json
from datetime import datetime, timezone
from collections import defaultdict
import statistics
import math
import sys

print("=" * 60)
print("REAL BACKTEST: TIME-BASED PATTERN ANALYSIS")
print("=" * 60)
print("Loading data... (this may take a minute)")
sys.stdout.flush()

# Load backtest data first (smaller, 17K markets)
BACKTEST_PATH = r"C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json"

print("\nLoading backtest_dataset_v1.json...")
sys.stdout.flush()
with open(BACKTEST_PATH, 'r', encoding='utf-8') as f:
    backtest_data = json.load(f)

print(f"Loaded {len(backtest_data)} markets with price histories")

# Create lookup
price_history_lookup = {}
for m in backtest_data:
    mid = str(m.get('market_id'))
    ph = m.get('price_history', [])
    if ph:
        price_history_lookup[mid] = {
            'ph': ph,
            'end_date': m.get('end_date'),
            'q': m.get('question', '')
        }

print(f"Markets with price history: {len(price_history_lookup)}")
sys.stdout.flush()

# Load outcomes from polymarket_complete
DATA_PATH = r"C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\polymarket_complete.json"

print("\nLoading polymarket_complete.json for outcomes...")
sys.stdout.flush()

# Process in streaming fashion
resolved_markets = []
outcomes_found = 0
yes_won_count = 0
no_won_count = 0

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    events_data = json.load(f)

print(f"Loaded {len(events_data)} events")
sys.stdout.flush()

for i, event in enumerate(events_data):
    if i % 20000 == 0:
        print(f"  Processing event {i}/{len(events_data)}...")
        sys.stdout.flush()
    
    if not event.get('closed'):
        continue
    
    for market in event.get('markets', []):
        market_id = str(market.get('market_id'))
        
        # Skip if no price history
        if market_id not in price_history_lookup:
            continue
        
        outcome_prices = market.get('outcome_prices', '')
        
        try:
            prices = json.loads(outcome_prices)
            if prices == ['1', '0'] or prices == [1, 0]:
                yes_won = True
                yes_won_count += 1
            elif prices == ['0', '1'] or prices == [0, 1]:
                yes_won = False
                no_won_count += 1
            else:
                continue
        except:
            continue
        
        outcomes_found += 1
        ph_data = price_history_lookup[market_id]
        resolved_markets.append({
            'yes_won': yes_won,
            'ph': ph_data['ph'],
            'end_date': ph_data['end_date'],
            'q': ph_data['q']
        })

print(f"\nOutcomes found: {outcomes_found}")
print(f"  YES won: {yes_won_count}")
print(f"  NO won: {no_won_count}")
print(f"Resolved markets with price history: {len(resolved_markets)}")
sys.stdout.flush()

# Trading costs
ROUNDTRIP_FEE = 0.04
SLIPPAGE = 0.015
TOTAL_COSTS = ROUNDTRIP_FEE + SLIPPAGE

print(f"\n=== COSTS: {TOTAL_COSTS*100:.1f}% total (4% fees + 1.5% slippage) ===")

# Analysis
time_of_day = defaultdict(lambda: {'r': [], 'w': 0, 'l': 0})
day_of_week = defaultdict(lambda: {'r': [], 'w': 0, 'l': 0})
days_to_close = defaultdict(lambda: {'r': [], 'w': 0, 'l': 0})
price_buckets = defaultdict(lambda: {'r': [], 'w': 0, 'l': 0})

total_trades = 0
print("\nAnalyzing trades...")
sys.stdout.flush()

for idx, market in enumerate(resolved_markets):
    if idx % 1000 == 0:
        print(f"  Market {idx}/{len(resolved_markets)}...")
        sys.stdout.flush()
    
    yes_won = market['yes_won']
    ph = market['ph']
    
    if len(ph) < 3:
        continue
    
    try:
        end_str = market.get('end_date', '')
        if end_str:
            end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        else:
            continue
    except:
        continue
    
    for point in ph:
        t = point.get('t')
        p = point.get('p')
        
        if t is None or p is None:
            continue
        if p < 0.03 or p > 0.97:
            continue
        
        try:
            entry_time = datetime.fromtimestamp(t, tz=timezone.utc)
        except:
            continue
        
        hour = entry_time.hour
        dow = entry_time.weekday()
        
        try:
            days_rem = (end_date - entry_time).total_seconds() / 86400
        except:
            days_rem = -1
        
        # Calculate return for buying YES
        if yes_won:
            gross_ret = (1.0 - p) / p
            net_ret = gross_ret - TOTAL_COSTS
        else:
            net_ret = -1.0 - TOTAL_COSTS
        
        win = net_ret > 0
        
        # Time of day
        time_of_day[hour]['r'].append(net_ret)
        if win:
            time_of_day[hour]['w'] += 1
        else:
            time_of_day[hour]['l'] += 1
        
        # Day of week
        day_of_week[dow]['r'].append(net_ret)
        if win:
            day_of_week[dow]['w'] += 1
        else:
            day_of_week[dow]['l'] += 1
        
        # Days to close
        if 0 <= days_rem <= 30:
            bucket = int(days_rem)
            days_to_close[bucket]['r'].append(net_ret)
            if win:
                days_to_close[bucket]['w'] += 1
            else:
                days_to_close[bucket]['l'] += 1
        
        # Price bucket
        pb = int(p * 10) / 10
        price_buckets[pb]['r'].append(net_ret)
        if win:
            price_buckets[pb]['w'] += 1
        else:
            price_buckets[pb]['l'] += 1
        
        total_trades += 1

print(f"\n{'='*60}")
print(f"TOTAL TRADE OPPORTUNITIES: {total_trades:,}")
print(f"{'='*60}")

def calc_stats(returns):
    if len(returns) < 30:
        return None
    mean = statistics.mean(returns)
    stdev = statistics.stdev(returns)
    if stdev == 0:
        return None
    stderr = stdev / math.sqrt(len(returns))
    t_stat = mean / stderr
    return {'mean': mean, 't_stat': t_stat, 'n': len(returns)}

# Results
print("\n" + "=" * 60)
print("TIME OF DAY (Hours UTC)")
print("=" * 60)
print(f"{'Hour':>4} | {'N':>8} | {'WinRate':>7} | {'AvgRet':>9} | {'T-stat':>7}")
print("-" * 50)

sig_hours = []
for hour in sorted(time_of_day.keys()):
    d = time_of_day[hour]
    n = len(d['r'])
    if n < 100:
        continue
    wr = d['w'] / n * 100
    avg = statistics.mean(d['r']) * 100
    stats = calc_stats(d['r'])
    t = stats['t_stat'] if stats else 0
    sig = "**" if abs(t) > 2.58 else "*" if abs(t) > 1.96 else ""
    if t > 1.96:
        sig_hours.append((hour, avg, t, n))
    print(f"{hour:4} | {n:8,} | {wr:6.1f}% | {avg:+8.2f}% | {t:+7.2f} {sig}")

print("\n" + "=" * 60)
print("DAY OF WEEK")
print("=" * 60)
dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
print(f"{'Day':>4} | {'N':>8} | {'WinRate':>7} | {'AvgRet':>9} | {'T-stat':>7}")
print("-" * 50)

sig_days = []
for dow in sorted(day_of_week.keys()):
    d = day_of_week[dow]
    n = len(d['r'])
    if n < 100:
        continue
    wr = d['w'] / n * 100
    avg = statistics.mean(d['r']) * 100
    stats = calc_stats(d['r'])
    t = stats['t_stat'] if stats else 0
    sig = "**" if abs(t) > 2.58 else "*" if abs(t) > 1.96 else ""
    if t > 1.96:
        sig_days.append((dow_names[dow], avg, t, n))
    print(f"{dow_names[dow]:>4} | {n:8,} | {wr:6.1f}% | {avg:+8.2f}% | {t:+7.2f} {sig}")

print("\n" + "=" * 60)
print("DAYS TO RESOLUTION")
print("=" * 60)
print(f"{'Days':>4} | {'N':>8} | {'WinRate':>7} | {'AvgRet':>9} | {'T-stat':>7}")
print("-" * 50)

sig_dtc = []
for days in sorted(days_to_close.keys()):
    d = days_to_close[days]
    n = len(d['r'])
    if n < 50:
        continue
    wr = d['w'] / n * 100
    avg = statistics.mean(d['r']) * 100
    stats = calc_stats(d['r'])
    t = stats['t_stat'] if stats else 0
    sig = "**" if abs(t) > 2.58 else "*" if abs(t) > 1.96 else ""
    if t > 1.96:
        sig_dtc.append((days, avg, t, n))
    print(f"{days:4} | {n:8,} | {wr:6.1f}% | {avg:+8.2f}% | {t:+7.2f} {sig}")

print("\n" + "=" * 60)
print("ENTRY PRICE BUCKETS")
print("=" * 60)
print(f"{'Price':>5} | {'N':>8} | {'WinRate':>7} | {'AvgRet':>9} | {'T-stat':>7}")
print("-" * 50)

sig_price = []
for price in sorted(price_buckets.keys()):
    d = price_buckets[price]
    n = len(d['r'])
    if n < 100:
        continue
    wr = d['w'] / n * 100
    avg = statistics.mean(d['r']) * 100
    stats = calc_stats(d['r'])
    t = stats['t_stat'] if stats else 0
    sig = "**" if abs(t) > 2.58 else "*" if abs(t) > 1.96 else ""
    if t > 1.96 and avg > 0:
        sig_price.append((price, avg, t, n))
    print(f"{price:5.1f} | {n:8,} | {wr:6.1f}% | {avg:+8.2f}% | {t:+7.2f} {sig}")

# Summary
print("\n" + "=" * 60)
print("SIGNIFICANT EDGES FOUND (p < 0.05)")
print("=" * 60)

print("\n📊 Time of Day:")
if sig_hours:
    for h, r, t, n in sig_hours:
        print(f"  Hour {h:02d} UTC: +{r:.2f}% (t={t:.2f}, n={n:,})")
else:
    print("  None found")

print("\n📊 Day of Week:")
if sig_days:
    for d, r, t, n in sig_days:
        print(f"  {d}: +{r:.2f}% (t={t:.2f}, n={n:,})")
else:
    print("  None found")

print("\n📊 Days to Resolution:")
if sig_dtc:
    for d, r, t, n in sig_dtc:
        print(f"  {d} days: +{r:.2f}% (t={t:.2f}, n={n:,})")
else:
    print("  None found")

print("\n📊 Price Entry Points (positive EV):")
if sig_price:
    for p, r, t, n in sig_price:
        print(f"  Buy at {p:.1f}: +{r:.2f}% (t={t:.2f}, n={n:,})")
else:
    print("  None found")

print("\n" + "=" * 60)
print("Analysis complete!")
