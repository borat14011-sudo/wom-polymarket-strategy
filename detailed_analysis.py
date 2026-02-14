#!/usr/bin/env python3
"""
Detailed Pattern Analysis for Polymarket Backtest Data
Shows all patterns, even those below threshold, for insight
"""

import json
from datetime import datetime
from collections import defaultdict
import statistics
from scipy import stats
import numpy as np

# Transaction cost
TX_COST = 0.04  # 4%
MIN_EDGE = 0.05  # 5% minimum edge
MIN_SAMPLES = 30
ALPHA = 0.05  # p-value threshold

def load_data(filepath):
    """Load the backtest dataset"""
    print("Loading data...")
    with open(filepath, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records")
    return data

def extract_features(data):
    """Extract features from each market"""
    markets = []
    
    for market in data:
        # Only analyze closed markets
        if not market.get('closed'):
            continue
            
        price_history = market.get('price_history', [])
        if not price_history:
            continue
        
        # Infer outcome from final price
        final_price = price_history[-1]['p']
        
        # Skip markets that didn't clearly resolve (middle prices)
        if 0.01 <= final_price <= 0.99:
            continue
        
        # Infer outcome: >0.99 = Yes, <0.01 = No
        outcome = 'Yes' if final_price > 0.99 else 'No'
        
        # Extract metadata
        market_info = {
            'market_id': market.get('market_id', 'unknown'),
            'question': market.get('question', ''),
            'volume': market.get('volume', 0),
            'outcome': outcome,
            'end_date': market.get('end_date'),
            'price_history': price_history,
            'final_price': final_price
        }
        
        # Add time features for each snapshot
        for snapshot in price_history:
            ts = snapshot['t']
            price = snapshot['p']
            dt = datetime.fromtimestamp(ts)
            
            snapshot['hour'] = dt.hour
            snapshot['day_of_week'] = dt.weekday()  # 0=Monday, 6=Sunday
            snapshot['price'] = price
        
        market_info['first_snapshot'] = price_history[0] if price_history else None
        market_info['last_snapshot'] = price_history[-1] if price_history else None
        
        markets.append(market_info)
    
    return markets

def analyze_all_patterns(markets):
    """Analyze all patterns comprehensively"""
    all_patterns = []
    
    # Day of week analysis
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_returns = defaultdict(list)
    
    # Hour of day analysis (grouped)
    hour_blocks = {
        'Early Morning (00-05)': list(range(0, 6)),
        'Morning (06-11)': list(range(6, 12)),
        'Afternoon (12-17)': list(range(12, 18)),
        'Evening (18-23)': list(range(18, 24))
    }
    hour_returns = defaultdict(list)
    
    # Price level analysis
    price_buckets = [
        (0, 0.1, 'Very Low (0-0.1)'),
        (0.1, 0.2, 'Low (0.1-0.2)'),
        (0.2, 0.3, 'Low-Mid (0.2-0.3)'),
        (0.3, 0.4, 'Mid-Low (0.3-0.4)'),
        (0.4, 0.6, 'Mid (0.4-0.6)'),
        (0.6, 0.7, 'Mid-High (0.6-0.7)'),
        (0.7, 0.8, 'High (0.7-0.8)'),
        (0.8, 0.9, 'Very High (0.8-0.9)'),
        (0.9, 1.0, 'Extreme (0.9-1.0)')
    ]
    price_returns = defaultdict(list)
    
    # Volume analysis
    volume_buckets = [
        (0, 1000, 'Very Low Volume (<$1K)'),
        (1000, 10000, 'Low Volume ($1K-$10K)'),
        (10000, 50000, 'Medium Volume ($10K-$50K)'),
        (50000, 100000, 'High Volume ($50K-$100K)'),
        (100000, float('inf'), 'Very High Volume (>$100K)')
    ]
    volume_returns = defaultdict(list)
    
    # Resolution timing analysis
    timing_returns = defaultdict(list)
    
    # Collect all data
    for market in markets:
        if not market['first_snapshot']:
            continue
        
        first_snap = market['first_snapshot']
        price = first_snap['price']
        dow = first_snap['day_of_week']
        hour = first_snap['hour']
        volume = market['volume']
        
        # Calculate return if buying Yes at first snapshot
        yes_win = market['outcome'] == 'Yes'
        if yes_win:
            ret = (1 / price) - 1 if price > 0 else 0
        else:
            ret = -1
        
        # Day of week
        dow_returns[dow].append(ret)
        
        # Hour of day
        for block_name, hours in hour_blocks.items():
            if hour in hours:
                hour_returns[block_name].append(ret)
                break
        
        # Price level
        for low, high, name in price_buckets:
            if low <= price < high:
                price_returns[name].append(ret)
                break
        
        # Volume
        for low, high, name in volume_buckets:
            if low <= volume < high:
                volume_returns[name].append(ret)
                break
        
        # Resolution timing
        if market['end_date']:
            try:
                first_ts = first_snap['t']
                end_dt = datetime.fromisoformat(market['end_date'].replace('Z', '+00:00'))
                resolved_ts = end_dt.timestamp()
                hours_to_resolution = (resolved_ts - first_ts) / 3600
                
                if hours_to_resolution >= 0:
                    if hours_to_resolution < 6:
                        timing_returns['< 6 hours'].append(ret)
                    elif hours_to_resolution < 24:
                        timing_returns['6-24 hours'].append(ret)
                    elif hours_to_resolution < 168:  # 1 week
                        timing_returns['1-7 days'].append(ret)
                    else:
                        timing_returns['> 7 days'].append(ret)
            except:
                pass
    
    # Analyze day of week patterns
    for dow in range(7):
        returns = dow_returns[dow]
        if len(returns) >= MIN_SAMPLES:
            mean_return = statistics.mean(returns)
            net_return = mean_return - TX_COST
            t_stat, p_value = stats.ttest_1samp(returns, -TX_COST)
            
            all_patterns.append({
                'type': 'Day of Week',
                'name': day_names[dow],
                'gross_edge': mean_return,
                'net_edge': net_return,
                'sample_size': len(returns),
                'p_value': p_value,
                'significant': p_value < ALPHA,
                'profitable': net_return > MIN_EDGE
            })
    
    # Analyze hour patterns
    for block_name, returns in hour_returns.items():
        if len(returns) >= MIN_SAMPLES:
            mean_return = statistics.mean(returns)
            net_return = mean_return - TX_COST
            t_stat, p_value = stats.ttest_1samp(returns, -TX_COST)
            
            all_patterns.append({
                'type': 'Time of Day',
                'name': block_name,
                'gross_edge': mean_return,
                'net_edge': net_return,
                'sample_size': len(returns),
                'p_value': p_value,
                'significant': p_value < ALPHA,
                'profitable': net_return > MIN_EDGE
            })
    
    # Analyze price level patterns
    for name, returns in price_returns.items():
        if len(returns) >= MIN_SAMPLES:
            mean_return = statistics.mean(returns)
            net_return = mean_return - TX_COST
            t_stat, p_value = stats.ttest_1samp(returns, -TX_COST)
            
            all_patterns.append({
                'type': 'Price Level',
                'name': name,
                'gross_edge': mean_return,
                'net_edge': net_return,
                'sample_size': len(returns),
                'p_value': p_value,
                'significant': p_value < ALPHA,
                'profitable': net_return > MIN_EDGE
            })
    
    # Analyze volume patterns
    for name, returns in volume_returns.items():
        if len(returns) >= MIN_SAMPLES:
            mean_return = statistics.mean(returns)
            net_return = mean_return - TX_COST
            t_stat, p_value = stats.ttest_1samp(returns, -TX_COST)
            
            all_patterns.append({
                'type': 'Volume',
                'name': name,
                'gross_edge': mean_return,
                'net_edge': net_return,
                'sample_size': len(returns),
                'p_value': p_value,
                'significant': p_value < ALPHA,
                'profitable': net_return > MIN_EDGE
            })
    
    # Analyze resolution timing patterns
    for name, returns in timing_returns.items():
        if len(returns) >= MIN_SAMPLES:
            mean_return = statistics.mean(returns)
            net_return = mean_return - TX_COST
            t_stat, p_value = stats.ttest_1samp(returns, -TX_COST)
            
            all_patterns.append({
                'type': 'Resolution Timing',
                'name': name,
                'gross_edge': mean_return,
                'net_edge': net_return,
                'sample_size': len(returns),
                'p_value': p_value,
                'significant': p_value < ALPHA,
                'profitable': net_return > MIN_EDGE
            })
    
    return all_patterns

def generate_report(patterns):
    """Generate comprehensive report"""
    
    # Filter patterns that meet criteria
    significant_patterns = [p for p in patterns if p['significant']]
    profitable_patterns = [p for p in patterns if p['profitable']]
    
    print("\n" + "="*60)
    print("PATTERN ANALYSIS REPORT")
    print("="*60)
    print(f"Total Patterns Analyzed: {len(patterns)}")
    print(f"Statistically Significant (p<0.05): {len(significant_patterns)}")
    print(f"Profitable (>5% edge after 4% costs): {len(profitable_patterns)}")
    print()
    
    if not profitable_patterns:
        print("NO PATTERNS FOUND WITH >5% EDGE AFTER 4% TRANSACTION COSTS")
        print("="*60)
        print("\nAll statistically significant patterns (below threshold):")
        print("-" * 60)
        
        # Group by type
        by_type = defaultdict(list)
        for p in significant_patterns:
            by_type[p['type']].append(p)
        
        for pattern_type, type_patterns in by_type.items():
            print(f"\n{pattern_type}:")
            for p in sorted(type_patterns, key=lambda x: x['net_edge'], reverse=True):
                print(f"  {p['name']}:")
                print(f"    Net Edge: {p['net_edge']:.2%} (Gross: {p['gross_edge']:.2%})")
                print(f"    Samples: {p['sample_size']}, P-value: {p['p_value']:.4f}")
    else:
        print("PROFITABLE PATTERNS FOUND:")
        print("="*60)
        for i, p in enumerate(sorted(profitable_patterns, key=lambda x: x['net_edge'], reverse=True), 1):
            print(f"\nPattern #{i}:")
            print(f"  Type: {p['type']}")
            print(f"  Name: {p['name']}")
            print(f"  Edge (gross): {p['gross_edge']:.2%}")
            print(f"  Edge (net after 4% costs): {p['net_edge']:.2%}")
            print(f"  Sample Size: {p['sample_size']}")
            print(f"  P-value: {p['p_value']:.6f}")
            print(f"  Confidence: {1 - p['p_value']:.2%}")
    
    # Summary statistics
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    # Overall market statistics
    total_returns = []
    for p in patterns:
        # Estimate total returns from sample size and mean
        total_returns.extend([p['gross_edge']] * p['sample_size'])
    
    if total_returns:
        overall_mean = statistics.mean(total_returns)
        overall_net = overall_mean - TX_COST
        print(f"Overall Market Return (gross): {overall_mean:.2%}")
        print(f"Overall Market Return (net after 4% costs): {overall_net:.2%}")
        print(f"Markets are {'PROFITABLE' if overall_net > 0 else 'UNPROFITABLE'} overall")
    
    print(f"\nKey Finding: {'NO' if not profitable_patterns else 'SOME'} exploitable patterns found")
    print("Recommendation: Continue random trading or find alternative strategies")

def main():
    filepath = 'polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json'
    
    # Load and process data
    data = load_data(filepath)
    markets = extract_features(data)
    
    print(f"\nAnalyzing {len(markets)} markets with inferred outcomes...")
    print(f"(Markets with clear final prices: <0.01 or >0.99)")
    
    # Run comprehensive analysis
    patterns = analyze_all_patterns(markets)
    
    # Generate report
    generate_report(patterns)

if __name__ == '__main__':
    main()
