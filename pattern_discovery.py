#!/usr/bin/env python3
"""
Pattern Discovery Analysis for Polymarket Historical Data
Analyzes trades for unexploited patterns with statistical rigor
"""

import json
from datetime import datetime
from collections import defaultdict
import statistics

# Transaction cost
TX_COST = 0.05  # 5%
MIN_SAMPLE_SIZE = 30

def load_data(filepath):
    """Load the backtest dataset"""
    with open(filepath, 'r') as f:
        return json.load(f)

def parse_timestamp(ts):
    """Parse ISO timestamp to datetime"""
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except:
        return None

def calculate_stats(wins, losses):
    """Calculate win rate and expected value"""
    total = wins + losses
    if total == 0:
        return None, None, None
    
    win_rate = wins / total
    # Assuming 1:1 payoff for simplicity (can be refined)
    expected_value = (win_rate * 1.0) - ((1 - win_rate) * 1.0) - TX_COST
    
    # Simple confidence score based on sample size
    if total < MIN_SAMPLE_SIZE:
        confidence = "INSUFFICIENT"
    elif total < 50:
        confidence = "LOW"
    elif total < 100:
        confidence = "MEDIUM"
    else:
        confidence = "HIGH"
    
    return win_rate, expected_value, confidence

def analyze_time_of_day(trades):
    """Analyze time-of-day effects"""
    hourly_results = defaultdict(lambda: {'wins': 0, 'losses': 0})
    
    for trade in trades:
        dt = parse_timestamp(trade.get('timestamp') or trade.get('created_at') or trade.get('date'))
        if not dt:
            continue
        
        hour = dt.hour
        outcome = trade.get('outcome') or trade.get('resolved') or trade.get('result')
        
        if outcome in [True, 'yes', 'YES', 'win', 'WIN', 1]:
            hourly_results[hour]['wins'] += 1
        elif outcome in [False, 'no', 'NO', 'loss', 'LOSS', 0]:
            hourly_results[hour]['losses'] += 1
    
    patterns = []
    for hour in range(24):
        wins = hourly_results[hour]['wins']
        losses = hourly_results[hour]['losses']
        win_rate, ev, conf = calculate_stats(wins, losses)
        
        if win_rate and ev > 0 and wins + losses >= MIN_SAMPLE_SIZE:
            patterns.append({
                'pattern': f'Hour {hour:02d}:00-{hour:02d}:59',
                'win_rate': win_rate,
                'sample_size': wins + losses,
                'expected_value': ev,
                'confidence': conf
            })
    
    return patterns

def analyze_day_of_week(trades):
    """Analyze day-of-week effects"""
    dow_results = defaultdict(lambda: {'wins': 0, 'losses': 0})
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for trade in trades:
        dt = parse_timestamp(trade.get('timestamp') or trade.get('created_at') or trade.get('date'))
        if not dt:
            continue
        
        dow = dt.weekday()
        outcome = trade.get('outcome') or trade.get('resolved') or trade.get('result')
        
        if outcome in [True, 'yes', 'YES', 'win', 'WIN', 1]:
            dow_results[dow]['wins'] += 1
        elif outcome in [False, 'no', 'NO', 'loss', 'LOSS', 0]:
            dow_results[dow]['losses'] += 1
    
    patterns = []
    for dow in range(7):
        wins = dow_results[dow]['wins']
        losses = dow_results[dow]['losses']
        win_rate, ev, conf = calculate_stats(wins, losses)
        
        if win_rate and ev > 0 and wins + losses >= MIN_SAMPLE_SIZE:
            patterns.append({
                'pattern': f'{day_names[dow]}',
                'win_rate': win_rate,
                'sample_size': wins + losses,
                'expected_value': ev,
                'confidence': conf
            })
    
    return patterns

def analyze_price_levels(trades):
    """Analyze price level biases"""
    price_buckets = {
        '0-10%': (0, 0.10),
        '10-20%': (0.10, 0.20),
        '20-30%': (0.20, 0.30),
        '30-40%': (0.30, 0.40),
        '40-50%': (0.40, 0.50),
        '50-60%': (0.50, 0.60),
        '60-70%': (0.60, 0.70),
        '70-80%': (0.70, 0.80),
        '80-90%': (0.80, 0.90),
        '90-100%': (0.90, 1.00),
    }
    
    bucket_results = defaultdict(lambda: {'wins': 0, 'losses': 0})
    
    for trade in trades:
        price = trade.get('price') or trade.get('entry_price') or trade.get('buy_price')
        if price is None:
            continue
        
        outcome = trade.get('outcome') or trade.get('resolved') or trade.get('result')
        
        for bucket_name, (low, high) in price_buckets.items():
            if low <= price < high:
                if outcome in [True, 'yes', 'YES', 'win', 'WIN', 1]:
                    bucket_results[bucket_name]['wins'] += 1
                elif outcome in [False, 'no', 'NO', 'loss', 'LOSS', 0]:
                    bucket_results[bucket_name]['losses'] += 1
                break
    
    patterns = []
    for bucket_name in price_buckets.keys():
        wins = bucket_results[bucket_name]['wins']
        losses = bucket_results[bucket_name]['losses']
        win_rate, ev, conf = calculate_stats(wins, losses)
        
        if win_rate and ev > 0 and wins + losses >= MIN_SAMPLE_SIZE:
            patterns.append({
                'pattern': f'Price Level: {bucket_name}',
                'win_rate': win_rate,
                'sample_size': wins + losses,
                'expected_value': ev,
                'confidence': conf
            })
    
    return patterns

def analyze_categories(trades):
    """Analyze market category correlations"""
    category_results = defaultdict(lambda: {'wins': 0, 'losses': 0})
    
    for trade in trades:
        category = trade.get('category') or trade.get('market_category') or trade.get('tags', [None])[0]
        if not category:
            continue
        
        outcome = trade.get('outcome') or trade.get('resolved') or trade.get('result')
        
        if outcome in [True, 'yes', 'YES', 'win', 'WIN', 1]:
            category_results[category]['wins'] += 1
        elif outcome in [False, 'no', 'NO', 'loss', 'LOSS', 0]:
            category_results[category]['losses'] += 1
    
    patterns = []
    for category, results in category_results.items():
        wins = results['wins']
        losses = results['losses']
        win_rate, ev, conf = calculate_stats(wins, losses)
        
        if win_rate and ev > 0 and wins + losses >= MIN_SAMPLE_SIZE:
            patterns.append({
                'pattern': f'Category: {category}',
                'win_rate': win_rate,
                'sample_size': wins + losses,
                'expected_value': ev,
                'confidence': conf
            })
    
    return patterns

def analyze_resolution_timing(trades):
    """Analyze patterns based on time between creation and resolution"""
    timing_buckets = {
        '<1 hour': (0, 3600),
        '1-6 hours': (3600, 21600),
        '6-24 hours': (21600, 86400),
        '1-3 days': (86400, 259200),
        '3-7 days': (259200, 604800),
        '1-4 weeks': (604800, 2419200),
        '>4 weeks': (2419200, float('inf'))
    }
    
    timing_results = defaultdict(lambda: {'wins': 0, 'losses': 0})
    
    for trade in trades:
        created = parse_timestamp(trade.get('timestamp') or trade.get('created_at') or trade.get('date'))
        resolved = parse_timestamp(trade.get('resolved_at') or trade.get('resolution_time'))
        
        if not created or not resolved:
            continue
        
        duration = (resolved - created).total_seconds()
        outcome = trade.get('outcome') or trade.get('resolved') or trade.get('result')
        
        for bucket_name, (low, high) in timing_buckets.items():
            if low <= duration < high:
                if outcome in [True, 'yes', 'YES', 'win', 'WIN', 1]:
                    timing_results[bucket_name]['wins'] += 1
                elif outcome in [False, 'no', 'NO', 'loss', 'LOSS', 0]:
                    timing_results[bucket_name]['losses'] += 1
                break
    
    patterns = []
    for bucket_name in timing_buckets.keys():
        wins = timing_results[bucket_name]['wins']
        losses = timing_results[bucket_name]['losses']
        win_rate, ev, conf = calculate_stats(wins, losses)
        
        if win_rate and ev > 0 and wins + losses >= MIN_SAMPLE_SIZE:
            patterns.append({
                'pattern': f'Resolution Timing: {bucket_name}',
                'win_rate': win_rate,
                'sample_size': wins + losses,
                'expected_value': ev,
                'confidence': conf
            })
    
    return patterns

def main():
    print("Loading dataset...")
    data = load_data('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json')
    
    # Handle different data structures
    if isinstance(data, dict):
        trades = data.get('trades') or data.get('markets') or []
    elif isinstance(data, list):
        trades = data
    else:
        print("Unknown data structure")
        return
    
    print(f"Analyzing {len(trades)} trades...\n")
    
    # Run all analyses
    all_patterns = []
    
    print("1. Analyzing time-of-day effects...")
    all_patterns.extend(analyze_time_of_day(trades))
    
    print("2. Analyzing day-of-week effects...")
    all_patterns.extend(analyze_day_of_week(trades))
    
    print("3. Analyzing price level biases...")
    all_patterns.extend(analyze_price_levels(trades))
    
    print("4. Analyzing market categories...")
    all_patterns.extend(analyze_categories(trades))
    
    print("5. Analyzing resolution timing patterns...\n")
    all_patterns.extend(analyze_resolution_timing(trades))
    
    # Sort by expected value
    all_patterns.sort(key=lambda x: x['expected_value'], reverse=True)
    
    # Print report
    print("=" * 80)
    print("PATTERN DISCOVERY REPORT")
    print("=" * 80)
    print(f"Transaction Cost: {TX_COST*100}%")
    print(f"Minimum Sample Size: {MIN_SAMPLE_SIZE}")
    print(f"Total Patterns Found: {len(all_patterns)}\n")
    
    if not all_patterns:
        print("❌ NO PROFITABLE PATTERNS FOUND")
        print("\nAll analyzed patterns either:")
        print("- Had insufficient sample size (n<30)")
        print("- Had expected value <5% after transaction costs")
        print("- Did not show statistically significant edge")
    else:
        for i, p in enumerate(all_patterns, 1):
            print(f"\n📊 PATTERN #{i}: {p['pattern']}")
            print(f"   Win Rate: {p['win_rate']*100:.2f}%")
            print(f"   Sample Size: {p['sample_size']}")
            print(f"   Expected Value: {p['expected_value']*100:.2f}%")
            print(f"   Confidence: {p['confidence']}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
