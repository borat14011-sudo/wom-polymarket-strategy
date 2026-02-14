#!/usr/bin/env python3
"""
Detailed Pattern Analysis - Show ALL patterns regardless of threshold
to understand market efficiency
"""

import json
from datetime import datetime
from collections import defaultdict
import statistics

TRANSACTION_COST = 0.04

def parse_timestamp(ts):
    """Parse various timestamp formats"""
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts)
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except:
        try:
            return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            return None

def analyze_all_patterns(data):
    """Comprehensive analysis showing all patterns"""
    
    # 1. Simple buy-and-hold from first to last price
    print("\n1. BUY-AND-HOLD BASELINE (First to Last Price)")
    print("-" * 80)
    
    profits = []
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
        prices = market['price_history']
        if len(prices) < 2:
            continue
        
        first_price = float(prices[0].get('price') or prices[0].get('p', 0))
        last_price = float(prices[-1].get('price') or prices[-1].get('p', 0))
        
        if first_price <= 0:
            continue
        
        outcome_val = 1 if market['outcome'] == 'YES' else 0
        if outcome_val == 1:
            profit = last_price - first_price
        else:
            profit = first_price - last_price
        
        profits.append(profit)
    
    if profits:
        avg_profit = statistics.mean(profits)
        win_rate = len([p for p in profits if p > 0]) / len(profits)
        ev_after_costs = avg_profit - TRANSACTION_COST
        
        print(f"Samples: {len(profits):,}")
        print(f"Win Rate: {win_rate:.2%}")
        print(f"Avg Profit (before costs): ${avg_profit:.4f}")
        print(f"EV After 4% Costs: ${ev_after_costs:.4f}")
        print(f"Edge: {ev_after_costs * 100:.2f}%")
        
        if ev_after_costs > 0:
            print("⚠️  Positive EV - but likely due to data collection bias")
        else:
            print("✅ Negative EV - expected for efficient markets with costs")
    
    # 2. Extreme price points
    print("\n2. EXTREME PRICE ANALYSIS")
    print("-" * 80)
    
    price_buckets = {
        'very_low': (0.0, 0.2),
        'low': (0.2, 0.4),
        'middle': (0.4, 0.6),
        'high': (0.6, 0.8),
        'very_high': (0.8, 1.0)
    }
    
    bucket_results = defaultdict(list)
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
        prices = market['price_history']
        if len(prices) < 2:
            continue
        
        first_price = float(prices[0].get('price') or prices[0].get('p', 0))
        last_price = float(prices[-1].get('price') or prices[-1].get('p', 0))
        
        if first_price <= 0:
            continue
        
        outcome_val = 1 if market['outcome'] == 'YES' else 0
        if outcome_val == 1:
            profit = last_price - first_price
        else:
            profit = first_price - last_price
        
        for bucket_name, (min_p, max_p) in price_buckets.items():
            if min_p <= first_price < max_p:
                bucket_results[bucket_name].append(profit)
                break
    
    for bucket_name in ['very_low', 'low', 'middle', 'high', 'very_high']:
        profits = bucket_results[bucket_name]
        if len(profits) >= 50:
            avg = statistics.mean(profits)
            wr = len([p for p in profits if p > 0]) / len(profits)
            ev = avg - TRANSACTION_COST
            print(f"{bucket_name:12s} ({price_buckets[bucket_name][0]:.1f}-{price_buckets[bucket_name][1]:.1f}): "
                  f"N={len(profits):4d} | WR={wr:.1%} | EV=${ev:7.4f} | Edge={ev*100:6.2f}%")
    
    # 3. Volume analysis
    print("\n3. VOLUME-BASED PATTERNS")
    print("-" * 80)
    
    volume_buckets = {
        'very_low': (0, 1000),
        'low': (1000, 10000),
        'medium': (10000, 100000),
        'high': (100000, 1000000),
        'very_high': (1000000, float('inf'))
    }
    
    vol_results = defaultdict(list)
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome') or not market.get('volume'):
            continue
        
        volume = float(market['volume'])
        prices = market['price_history']
        if len(prices) < 2:
            continue
        
        first_price = float(prices[0].get('price') or prices[0].get('p', 0))
        last_price = float(prices[-1].get('price') or prices[-1].get('p', 0))
        
        if first_price <= 0:
            continue
        
        outcome_val = 1 if market['outcome'] == 'YES' else 0
        if outcome_val == 1:
            profit = last_price - first_price
        else:
            profit = first_price - last_price
        
        for bucket_name, (min_v, max_v) in volume_buckets.items():
            if min_v <= volume < max_v:
                vol_results[bucket_name].append(profit)
                break
    
    for bucket_name in ['very_low', 'low', 'medium', 'high', 'very_high']:
        profits = vol_results[bucket_name]
        if len(profits) >= 50:
            avg = statistics.mean(profits)
            wr = len([p for p in profits if p > 0]) / len(profits)
            ev = avg - TRANSACTION_COST
            print(f"{bucket_name:12s}: N={len(profits):5d} | WR={wr:.1%} | "
                  f"EV=${ev:7.4f} | Edge={ev*100:6.2f}%")
    
    # 4. Market duration
    print("\n4. MARKET DURATION ANALYSIS")
    print("-" * 80)
    
    duration_results = defaultdict(list)
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
        
        start = parse_timestamp(market.get('start_date'))
        end = parse_timestamp(market.get('end_date'))
        
        if not start or not end:
            continue
        
        duration_days = (end - start).total_seconds() / 86400
        
        prices = market['price_history']
        if len(prices) < 2:
            continue
        
        first_price = float(prices[0].get('price') or prices[0].get('p', 0))
        last_price = float(prices[-1].get('price') or prices[-1].get('p', 0))
        
        if first_price <= 0:
            continue
        
        outcome_val = 1 if market['outcome'] == 'YES' else 0
        if outcome_val == 1:
            profit = last_price - first_price
        else:
            profit = first_price - last_price
        
        if duration_days < 1:
            bucket = '< 1 day'
        elif duration_days < 7:
            bucket = '1-7 days'
        elif duration_days < 30:
            bucket = '7-30 days'
        elif duration_days < 90:
            bucket = '30-90 days'
        else:
            bucket = '> 90 days'
        
        duration_results[bucket].append(profit)
    
    for bucket in ['< 1 day', '1-7 days', '7-30 days', '30-90 days', '> 90 days']:
        if bucket in duration_results:
            profits = duration_results[bucket]
            if len(profits) >= 50:
                avg = statistics.mean(profits)
                wr = len([p for p in profits if p > 0]) / len(profits)
                ev = avg - TRANSACTION_COST
                print(f"{bucket:12s}: N={len(profits):5d} | WR={wr:.1%} | "
                      f"EV=${ev:7.4f} | Edge={ev*100:6.2f}%")
    
    # 5. Volatility patterns
    print("\n5. VOLATILITY ANALYSIS (Price Range)")
    print("-" * 80)
    
    volatility_results = defaultdict(list)
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
        
        prices = market['price_history']
        if len(prices) < 3:
            continue
        
        price_values = [float(p.get('price') or p.get('p', 0)) for p in prices]
        price_values = [p for p in price_values if p > 0]
        
        if len(price_values) < 3:
            continue
        
        price_range = max(price_values) - min(price_values)
        
        first_price = price_values[0]
        last_price = price_values[-1]
        
        outcome_val = 1 if market['outcome'] == 'YES' else 0
        if outcome_val == 1:
            profit = last_price - first_price
        else:
            profit = first_price - last_price
        
        if price_range < 0.1:
            bucket = 'very_stable'
        elif price_range < 0.3:
            bucket = 'stable'
        elif price_range < 0.5:
            bucket = 'moderate'
        else:
            bucket = 'volatile'
        
        volatility_results[bucket].append(profit)
    
    for bucket in ['very_stable', 'stable', 'moderate', 'volatile']:
        if bucket in volatility_results:
            profits = volatility_results[bucket]
            if len(profits) >= 50:
                avg = statistics.mean(profits)
                wr = len([p for p in profits if p > 0]) / len(profits)
                ev = avg - TRANSACTION_COST
                print(f"{bucket:12s}: N={len(profits):5d} | WR={wr:.1%} | "
                      f"EV=${ev:7.4f} | Edge={ev*100:6.2f}%")

def main():
    print("Loading backtest dataset...")
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data):,} markets")
    print("\n" + "="*80)
    print("DETAILED PATTERN ANALYSIS")
    print("All patterns shown, regardless of profitability threshold")
    print("="*80)
    
    analyze_all_patterns(data)
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("""
This analysis shows ALL patterns in the dataset, even unprofitable ones.

Key Findings:
1. If no pattern shows >5% edge after 4% costs, markets are efficient
2. Small positive edges (<5%) are likely noise/overfitting
3. Patterns with high sample counts but low edges suggest market sophistication
4. The 4% transaction cost is a significant barrier to profitability

Recommendation: Focus on finding information edges (better prediction models)
rather than timing/pattern-based strategies.
""")

if __name__ == '__main__':
    main()
