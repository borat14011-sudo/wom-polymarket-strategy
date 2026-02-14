#!/usr/bin/env python3
"""
Pattern Analysis for Polymarket Backtest Dataset
Analyzes for new trading patterns with >100 samples and >5% edge after 4% costs
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Constants
TRANSACTION_COST = 0.04  # 4% total transaction cost
MIN_SAMPLES = 100
MIN_EDGE = 0.05  # 5% edge after costs

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

def analyze_time_of_day_bias(data):
    """Analyze if certain hours show consistent price movements"""
    hourly_patterns = defaultdict(list)
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
            
        prices = market['price_history']
        if len(prices) < 2:
            continue
            
        # Analyze price movements by hour
        for i in range(len(prices) - 1):
            current = prices[i]
            next_price = prices[i + 1]
            
            timestamp = parse_timestamp(current.get('timestamp') or current.get('t'))
            if not timestamp:
                continue
                
            hour = timestamp.hour
            price_current = float(current.get('price') or current.get('p', 0))
            price_next = float(next_price.get('price') or next_price.get('p', 0))
            
            if price_current > 0 and price_next > 0:
                price_change = (price_next - price_current) / price_current
                
                # Record outcome-aligned movements
                outcome_val = 1 if market['outcome'] == 'YES' else 0
                if outcome_val == 1:  # Market resolved YES
                    profit = price_next - price_current  # Going long
                else:  # Market resolved NO
                    profit = price_current - price_next  # Going short
                    
                hourly_patterns[hour].append({
                    'change': price_change,
                    'profit': profit,
                    'price': price_current
                })
    
    # Calculate stats for each hour
    results = []
    for hour in range(24):
        samples = hourly_patterns[hour]
        if len(samples) < MIN_SAMPLES:
            continue
            
        avg_profit = statistics.mean([s['profit'] for s in samples])
        win_rate = len([s for s in samples if s['profit'] > 0]) / len(samples)
        expected_value = avg_profit - TRANSACTION_COST
        
        if expected_value > MIN_EDGE:
            results.append({
                'hour': hour,
                'samples': len(samples),
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'expected_value': expected_value,
                'edge_pct': expected_value * 100
            })
    
    return sorted(results, key=lambda x: x['expected_value'], reverse=True)

def analyze_day_of_week(data):
    """Analyze day-of-week effects"""
    dow_patterns = defaultdict(list)
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
            
        prices = market['price_history']
        if len(prices) < 2:
            continue
            
        # Get start day of week
        start_date = parse_timestamp(market.get('start_date'))
        if not start_date:
            continue
            
        dow = start_date.weekday()  # 0=Monday, 6=Sunday
        
        # Calculate overall market performance
        first_price = float(prices[0].get('price') or prices[0].get('p', 0))
        last_price = float(prices[-1].get('price') or prices[-1].get('p', 0))
        
        if first_price > 0:
            outcome_val = 1 if market['outcome'] == 'YES' else 0
            
            # Simulate buying at first price
            if outcome_val == 1:
                profit = last_price - first_price
            else:
                profit = first_price - last_price
                
            dow_patterns[dow].append({
                'profit': profit,
                'first_price': first_price,
                'last_price': last_price
            })
    
    # Calculate stats
    results = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for dow in range(7):
        samples = dow_patterns[dow]
        if len(samples) < MIN_SAMPLES:
            continue
            
        avg_profit = statistics.mean([s['profit'] for s in samples])
        win_rate = len([s for s in samples if s['profit'] > 0]) / len(samples)
        expected_value = avg_profit - TRANSACTION_COST
        
        if expected_value > MIN_EDGE:
            results.append({
                'day': days[dow],
                'samples': len(samples),
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'expected_value': expected_value,
                'edge_pct': expected_value * 100
            })
    
    return sorted(results, key=lambda x: x['expected_value'], reverse=True)

def analyze_price_momentum(data):
    """Analyze momentum signals - does recent price movement predict continued movement?"""
    momentum_patterns = {
        'strong_up': [],    # >10% gain in last period
        'moderate_up': [],  # 5-10% gain
        'neutral': [],      # -5% to 5%
        'moderate_down': [], # -10% to -5%
        'strong_down': []   # <-10%
    }
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
            
        prices = market['price_history']
        if len(prices) < 3:  # Need at least 3 points
            continue
            
        # Calculate momentum from first 1/3 of price history
        momentum_window = max(2, len(prices) // 3)
        
        first_price = float(prices[0].get('price') or prices[0].get('p', 0))
        momentum_price = float(prices[momentum_window].get('price') or prices[momentum_window].get('p', 0))
        final_price = float(prices[-1].get('price') or prices[-1].get('p', 0))
        
        if first_price <= 0 or momentum_price <= 0:
            continue
            
        # Momentum indicator
        momentum_change = (momentum_price - first_price) / first_price
        
        # Future profit (from momentum point to end)
        outcome_val = 1 if market['outcome'] == 'YES' else 0
        if outcome_val == 1:
            profit = final_price - momentum_price
        else:
            profit = momentum_price - final_price
            
        # Categorize momentum
        if momentum_change > 0.10:
            category = 'strong_up'
        elif momentum_change > 0.05:
            category = 'moderate_up'
        elif momentum_change > -0.05:
            category = 'neutral'
        elif momentum_change > -0.10:
            category = 'moderate_down'
        else:
            category = 'strong_down'
            
        momentum_patterns[category].append({
            'momentum': momentum_change,
            'profit': profit,
            'entry_price': momentum_price
        })
    
    # Calculate stats
    results = []
    for category, samples in momentum_patterns.items():
        if len(samples) < MIN_SAMPLES:
            continue
            
        avg_profit = statistics.mean([s['profit'] for s in samples])
        win_rate = len([s for s in samples if s['profit'] > 0]) / len(samples)
        expected_value = avg_profit - TRANSACTION_COST
        
        if expected_value > MIN_EDGE:
            results.append({
                'pattern': category,
                'samples': len(samples),
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'expected_value': expected_value,
                'edge_pct': expected_value * 100
            })
    
    return sorted(results, key=lambda x: x['expected_value'], reverse=True)

def analyze_resolution_timing(data):
    """Analyze if time until resolution affects profitability"""
    timing_patterns = {
        'very_short': [],   # <1 day
        'short': [],        # 1-7 days
        'medium': [],       # 7-30 days
        'long': [],         # 30-90 days
        'very_long': []     # >90 days
    }
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome'):
            continue
            
        start_date = parse_timestamp(market.get('start_date'))
        end_date = parse_timestamp(market.get('end_date'))
        
        if not start_date or not end_date:
            continue
            
        duration = (end_date - start_date).total_seconds() / 86400  # days
        
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
            
        # Categorize by duration
        if duration < 1:
            category = 'very_short'
        elif duration < 7:
            category = 'short'
        elif duration < 30:
            category = 'medium'
        elif duration < 90:
            category = 'long'
        else:
            category = 'very_long'
            
        timing_patterns[category].append({
            'duration': duration,
            'profit': profit,
            'price': first_price
        })
    
    # Calculate stats
    results = []
    for category, samples in timing_patterns.items():
        if len(samples) < MIN_SAMPLES:
            continue
            
        avg_profit = statistics.mean([s['profit'] for s in samples])
        win_rate = len([s for s in samples if s['profit'] > 0]) / len(samples)
        expected_value = avg_profit - TRANSACTION_COST
        
        if expected_value > MIN_EDGE:
            results.append({
                'duration_category': category,
                'samples': len(samples),
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'expected_value': expected_value,
                'edge_pct': expected_value * 100,
                'avg_duration_days': statistics.mean([s['duration'] for s in samples])
            })
    
    return sorted(results, key=lambda x: x['expected_value'], reverse=True)

def extract_category_from_question(question):
    """Extract market category from question text"""
    question_lower = question.lower()
    
    categories = {
        'crypto': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol'],
        'politics': ['election', 'president', 'trump', 'biden', 'senate', 'congress', 'vote'],
        'sports': ['nfl', 'nba', 'mlb', 'super bowl', 'championship', 'team', 'game'],
        'finance': ['stock', 'fed', 'rate', 'market', 's&p', 'dow'],
        'technology': ['ai', 'openai', 'google', 'apple', 'tech', 'agi'],
        'entertainment': ['movie', 'oscar', 'emmy', 'box office', 'album'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in question_lower for keyword in keywords):
            return category
    
    return 'other'

def analyze_category_correlation(data):
    """Analyze if certain market categories have better win rates"""
    category_patterns = defaultdict(list)
    
    for market in data:
        if not market.get('price_history') or not market.get('outcome') or not market.get('question'):
            continue
            
        category = extract_category_from_question(market['question'])
        
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
            
        category_patterns[category].append({
            'profit': profit,
            'price': first_price
        })
    
    # Calculate stats
    results = []
    for category, samples in category_patterns.items():
        if len(samples) < MIN_SAMPLES:
            continue
            
        avg_profit = statistics.mean([s['profit'] for s in samples])
        win_rate = len([s for s in samples if s['profit'] > 0]) / len(samples)
        expected_value = avg_profit - TRANSACTION_COST
        
        if expected_value > MIN_EDGE:
            results.append({
                'category': category,
                'samples': len(samples),
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'expected_value': expected_value,
                'edge_pct': expected_value * 100
            })
    
    return sorted(results, key=lambda x: x['expected_value'], reverse=True)

def main():
    print("Loading backtest dataset...")
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} markets\n")
    print("="*80)
    print("PATTERN ANALYSIS REPORT")
    print("Minimum samples: 100 | Minimum edge: 5% | Transaction costs: 4%")
    print("="*80)
    
    # Time of day analysis
    print("\n1. TIME-OF-DAY BIAS")
    print("-" * 80)
    tod_results = analyze_time_of_day_bias(data)
    if tod_results:
        for r in tod_results:
            print(f"Hour {r['hour']:02d}:00 - Samples: {r['samples']:,} | Win Rate: {r['win_rate']:.1%} | "
                  f"Edge: {r['edge_pct']:.2f}% | EV: ${r['expected_value']:.4f}")
    else:
        print("❌ No patterns found meeting criteria (>100 samples, >5% edge)")
    
    # Day of week
    print("\n2. DAY-OF-WEEK EFFECTS")
    print("-" * 80)
    dow_results = analyze_day_of_week(data)
    if dow_results:
        for r in dow_results:
            print(f"{r['day']:10s} - Samples: {r['samples']:,} | Win Rate: {r['win_rate']:.1%} | "
                  f"Edge: {r['edge_pct']:.2f}% | EV: ${r['expected_value']:.4f}")
    else:
        print("❌ No patterns found meeting criteria (>100 samples, >5% edge)")
    
    # Momentum
    print("\n3. PRICE MOMENTUM SIGNALS")
    print("-" * 80)
    momentum_results = analyze_price_momentum(data)
    if momentum_results:
        for r in momentum_results:
            print(f"{r['pattern']:15s} - Samples: {r['samples']:,} | Win Rate: {r['win_rate']:.1%} | "
                  f"Edge: {r['edge_pct']:.2f}% | EV: ${r['expected_value']:.4f}")
    else:
        print("❌ No patterns found meeting criteria (>100 samples, >5% edge)")
    
    # Resolution timing
    print("\n4. RESOLUTION TIMING PATTERNS")
    print("-" * 80)
    timing_results = analyze_resolution_timing(data)
    if timing_results:
        for r in timing_results:
            print(f"{r['duration_category']:12s} (~{r['avg_duration_days']:.1f}d) - Samples: {r['samples']:,} | "
                  f"Win Rate: {r['win_rate']:.1%} | Edge: {r['edge_pct']:.2f}% | EV: ${r['expected_value']:.4f}")
    else:
        print("❌ No patterns found meeting criteria (>100 samples, >5% edge)")
    
    # Category correlation
    print("\n5. MARKET CATEGORY CORRELATIONS")
    print("-" * 80)
    category_results = analyze_category_correlation(data)
    if category_results:
        for r in category_results:
            print(f"{r['category']:15s} - Samples: {r['samples']:,} | Win Rate: {r['win_rate']:.1%} | "
                  f"Edge: {r['edge_pct']:.2f}% | EV: ${r['expected_value']:.4f}")
    else:
        print("❌ No patterns found meeting criteria (>100 samples, >5% edge)")
    
    # Summary
    print("\n" + "="*80)
    print("OVERFITTING CHECK")
    print("="*80)
    total_patterns = len(tod_results) + len(dow_results) + len(momentum_results) + len(timing_results) + len(category_results)
    
    if total_patterns == 0:
        print("✅ GOOD: No exploitable patterns found. This suggests:")
        print("   - Markets are efficiently priced")
        print("   - 4% transaction costs eliminate most edges")
        print("   - No obvious timing or category biases")
    elif total_patterns <= 3:
        print(f"⚠️  CAUTION: Found {total_patterns} pattern(s). Possible legitimate signals, but:")
        print("   - Could be data snooping artifacts")
        print("   - Recommend forward testing before trading")
        print("   - Watch for regime changes")
    else:
        print(f"🚨 WARNING: Found {total_patterns} patterns. This is suspicious!")
        print("   - Likely overfitting to historical data")
        print("   - Multiple testing problem (looked at many patterns)")
        print("   - High risk these won't work out-of-sample")
        print("   - DO NOT TRADE without extensive validation")

if __name__ == '__main__':
    main()
