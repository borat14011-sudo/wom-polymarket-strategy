#!/usr/bin/env python3
"""
Discover NEW patterns in Polymarket data that haven't been exploited yet
Uses final price inference: >0.9 = YES, <0.1 = NO
"""

import json
from datetime import datetime
from collections import defaultdict
import re

# Constants
TX_COST = 0.05
MIN_SAMPLE = 30
EXISTING_PATTERNS = {
    'BTC_TIME_OF_DAY', 'FADE_HIGH_0.7', 'MUSK_FADE_EXTREMES', 'WEATHER_FADE_LONGSHOTS'
}

def load_data():
    with open('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json') as f:
        return json.load(f)

def infer_outcome(market):
    """Infer outcome from final price"""
    if not market.get('closed') or not market.get('price_history'):
        return None
    final_price = market['price_history'][-1]['p']
    if final_price > 0.9:
        return 'YES'
    elif final_price < 0.1:
        return 'NO'
    return None

def get_entry_price(market, percentile=0.2):
    """Get early entry price (20th percentile by default)"""
    if not market.get('price_history') or len(market['price_history']) < 5:
        return None
    idx = max(1, int(len(market['price_history']) * percentile))
    return market['price_history'][idx]['p']

def calculate_pnl(entry_price, outcome, direction='YES'):
    """Calculate P&L for a trade"""
    if direction == 'YES':
        if outcome == 'YES':
            return (1 - entry_price) / entry_price - TX_COST
        else:
            return -1 - TX_COST
    else:  # NO
        if outcome == 'NO':
            return (1 - entry_price) / entry_price - TX_COST
        else:
            return -1 - TX_COST

def get_category(question):
    """Extract category from question"""
    q_lower = question.lower()
    if 'bitcoin' in q_lower or 'btc' in q_lower:
        return 'BTC'
    elif 'ethereum' in q_lower or 'eth' in q_lower:
        return 'ETH'
    elif 'solana' in q_lower or 'sol' in q_lower:
        return 'SOL'
    elif any(coin in q_lower for coin in ['crypto', 'coin', 'token', 'defi']):
        return 'Crypto-Other'
    elif 'elon' in q_lower or 'musk' in q_lower:
        return 'Musk'
    elif 'trump' in q_lower:
        return 'Trump'
    elif any(w in q_lower for w in ['temperature', 'weather', 'rain', 'snow']):
        return 'Weather'
    elif any(w in q_lower for w in ['nba', 'nfl', 'soccer', 'football', 'basketball']):
        return 'Sports'
    elif any(w in q_lower for w in ['stock', 'spy', 'nasdaq', 'dow']):
        return 'Stocks'
    return 'Other'

def get_timestamp(market):
    """Get market start timestamp"""
    try:
        return datetime.fromisoformat(market['start_date'].replace('Z', '+00:00'))
    except:
        return None

def print_pattern(name, wins, losses, description=""):
    """Print pattern if it meets criteria"""
    total = wins + losses
    if total < MIN_SAMPLE:
        return None
    
    win_rate = wins / total
    # Simplified EV calculation
    ev = (win_rate * 1.0) - ((1 - win_rate) * 1.0) - TX_COST
    
    if ev <= 0:
        return None
    
    confidence = "HIGH" if total >= 100 else "MEDIUM" if total >= 50 else "LOW"
    
    return {
        'pattern': name,
        'description': description,
        'win_rate': win_rate,
        'sample_size': total,
        'expected_value': ev,
        'confidence': confidence,
        'wins': wins,
        'losses': losses
    }

print("Loading 17,324 markets...")
markets = load_data()

# Filter to closed markets with inferrable outcomes
valid_markets = []
for m in markets:
    outcome = infer_outcome(m)
    if outcome:
        valid_markets.append((m, outcome))

print(f"Valid markets for analysis: {len(valid_markets)} (~{len(valid_markets)/len(markets)*100:.1f}%)")
print("\nSearching for NEW patterns...\n")

patterns = []

# ========================================
# 1. DAY OF WEEK EFFECTS
# ========================================
print("[1/6] Analyzing day-of-week effects...")
dow_results = {i: {'YES_wins': 0, 'YES_losses': 0, 'NO_wins': 0, 'NO_losses': 0} for i in range(7)}
dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

for market, outcome in valid_markets:
    dt = get_timestamp(market)
    if not dt:
        continue
    entry = get_entry_price(market, 0.2)
    if not entry or entry >= 0.9 or entry <= 0.1:
        continue
    
    dow = dt.weekday()
    
    # Try YES direction
    pnl_yes = calculate_pnl(entry, outcome, 'YES')
    if pnl_yes > 0:
        dow_results[dow]['YES_wins'] += 1
    else:
        dow_results[dow]['YES_losses'] += 1
    
    # Try NO direction
    pnl_no = calculate_pnl(entry, outcome, 'NO')
    if pnl_no > 0:
        dow_results[dow]['NO_wins'] += 1
    else:
        dow_results[dow]['NO_losses'] += 1

for dow in range(7):
    for direction in ['YES', 'NO']:
        wins = dow_results[dow][f'{direction}_wins']
        losses = dow_results[dow][f'{direction}_losses']
        p = print_pattern(
            f"{dow_names[dow]} - Always {direction}",
            wins, losses,
            f"Trade {direction} on all markets opening on {dow_names[dow]}"
        )
        if p:
            patterns.append(p)

# ========================================
# 2. GRANULAR PRICE LEVEL ANALYSIS
# ========================================
print("[2/6] Analyzing granular price levels...")
price_buckets = [
    (0.05, 0.15, '5-15%'),
    (0.15, 0.25, '15-25%'),
    (0.25, 0.35, '25-35%'),
    (0.35, 0.45, '35-45%'),
    (0.45, 0.55, '45-55%'),
    (0.55, 0.65, '55-65%'),
    (0.65, 0.75, '65-75%'),
    (0.75, 0.85, '75-85%'),
    (0.85, 0.95, '85-95%'),
]

for low, high, label in price_buckets:
    yes_wins = yes_losses = no_wins = no_losses = 0
    
    for market, outcome in valid_markets:
        entry = get_entry_price(market, 0.2)
        if not entry or not (low <= entry < high):
            continue
        
        pnl_yes = calculate_pnl(entry, outcome, 'YES')
        if pnl_yes > 0:
            yes_wins += 1
        else:
            yes_losses += 1
        
        pnl_no = calculate_pnl(entry, outcome, 'NO')
        if pnl_no > 0:
            no_wins += 1
        else:
            no_losses += 1
    
    p = print_pattern(
        f"Entry Price {label} - YES",
        yes_wins, yes_losses,
        f"Buy YES when entry price is {label}"
    )
    if p:
        patterns.append(p)
    
    p = print_pattern(
        f"Entry Price {label} - NO",
        no_wins, no_losses,
        f"Buy NO when entry price is {label}"
    )
    if p:
        patterns.append(p)

# ========================================
# 3. MARKET MATURITY (TIME TO RESOLUTION)
# ========================================
print("[3/6] Analyzing market maturity patterns...")
maturity_buckets = [
    (0, 86400, '<1 day'),
    (86400, 259200, '1-3 days'),
    (259200, 604800, '3-7 days'),
    (604800, 1209600, '1-2 weeks'),
    (1209600, 2592000, '2-4 weeks'),
    (2592000, float('inf'), '>4 weeks'),
]

for low, high, label in maturity_buckets:
    yes_wins = yes_losses = no_wins = no_losses = 0
    
    for market, outcome in valid_markets:
        start = get_timestamp(market)
        try:
            end = datetime.fromisoformat(market['end_date'].replace('Z', '+00:00'))
        except:
            continue
        
        if not start or not end:
            continue
        
        duration = (end - start).total_seconds()
        if not (low <= duration < high):
            continue
        
        entry = get_entry_price(market, 0.2)
        if not entry or entry >= 0.9 or entry <= 0.1:
            continue
        
        pnl_yes = calculate_pnl(entry, outcome, 'YES')
        if pnl_yes > 0:
            yes_wins += 1
        else:
            yes_losses += 1
        
        pnl_no = calculate_pnl(entry, outcome, 'NO')
        if pnl_no > 0:
            no_wins += 1
        else:
            no_losses += 1
    
    p = print_pattern(
        f"Market Maturity {label} - YES",
        yes_wins, yes_losses,
        f"Buy YES on markets resolving in {label}"
    )
    if p:
        patterns.append(p)
    
    p = print_pattern(
        f"Market Maturity {label} - NO",
        no_wins, no_losses,
        f"Buy NO on markets resolving in {label}"
    )
    if p:
        patterns.append(p)

# ========================================
# 4. CATEGORY-SPECIFIC PATTERNS (NEW CATEGORIES)
# ========================================
print("[4/6] Analyzing category-specific patterns...")
category_results = defaultdict(lambda: {'YES_wins': 0, 'YES_losses': 0, 'NO_wins': 0, 'NO_losses': 0})

for market, outcome in valid_markets:
    cat = get_category(market['question'])
    if cat in ['Musk', 'Weather']:  # Skip already exploited categories
        continue
    
    entry = get_entry_price(market, 0.2)
    if not entry or entry >= 0.9 or entry <= 0.1:
        continue
    
    pnl_yes = calculate_pnl(entry, outcome, 'YES')
    if pnl_yes > 0:
        category_results[cat]['YES_wins'] += 1
    else:
        category_results[cat]['YES_losses'] += 1
    
    pnl_no = calculate_pnl(entry, outcome, 'NO')
    if pnl_no > 0:
        category_results[cat]['NO_wins'] += 1
    else:
        category_results[cat]['NO_losses'] += 1

for cat, results in category_results.items():
    for direction in ['YES', 'NO']:
        wins = results[f'{direction}_wins']
        losses = results[f'{direction}_losses']
        p = print_pattern(
            f"Category: {cat} - Always {direction}",
            wins, losses,
            f"Trade {direction} on all {cat} markets"
        )
        if p:
            patterns.append(p)

# ========================================
# 5. VOLUME PATTERNS
# ========================================
print("[5/6] Analyzing volume-based patterns...")
volume_buckets = [
    (0, 1000, 'Very Low <$1K'),
    (1000, 10000, 'Low $1-10K'),
    (10000, 100000, 'Medium $10-100K'),
    (100000, float('inf'), 'High >$100K'),
]

for low, high, label in volume_buckets:
    yes_wins = yes_losses = no_wins = no_losses = 0
    
    for market, outcome in valid_markets:
        volume = market.get('volume', 0)
        if not (low <= volume < high):
            continue
        
        entry = get_entry_price(market, 0.2)
        if not entry or entry >= 0.9 or entry <= 0.1:
            continue
        
        pnl_yes = calculate_pnl(entry, outcome, 'YES')
        if pnl_yes > 0:
            yes_wins += 1
        else:
            yes_losses += 1
        
        pnl_no = calculate_pnl(entry, outcome, 'NO')
        if pnl_no > 0:
            no_wins += 1
        else:
            no_losses += 1
    
    p = print_pattern(
        f"Volume {label} - YES",
        yes_wins, yes_losses,
        f"Buy YES on {label} volume markets"
    )
    if p:
        patterns.append(p)
    
    p = print_pattern(
        f"Volume {label} - NO",
        no_wins, no_losses,
        f"Buy NO on {label} volume markets"
    )
    if p:
        patterns.append(p)

# ========================================
# 6. PRICE MOMENTUM PATTERNS
# ========================================
print("[6/6] Analyzing price momentum patterns...")
momentum_wins = {'up': 0, 'down': 0, 'flat': 0}
momentum_losses = {'up': 0, 'down': 0, 'flat': 0}

for market, outcome in valid_markets:
    if not market.get('price_history') or len(market['price_history']) < 10:
        continue
    
    # Compare price at 20% vs 50% of history
    idx_early = int(len(market['price_history']) * 0.2)
    idx_mid = int(len(market['price_history']) * 0.5)
    
    price_early = market['price_history'][idx_early]['p']
    price_mid = market['price_history'][idx_mid]['p']
    
    if price_mid > price_early * 1.1:
        momentum = 'up'
        direction = 'YES'
    elif price_mid < price_early * 0.9:
        momentum = 'down'
        direction = 'NO'
    else:
        momentum = 'flat'
        continue  # Skip flat markets
    
    entry = price_mid
    if entry >= 0.9 or entry <= 0.1:
        continue
    
    pnl = calculate_pnl(entry, outcome, direction)
    if pnl > 0:
        momentum_wins[momentum] += 1
    else:
        momentum_losses[momentum] += 1

for momentum in ['up', 'down']:
    direction = 'YES' if momentum == 'up' else 'NO'
    p = print_pattern(
        f"Price Momentum {momentum.upper()} - Follow",
        momentum_wins[momentum], momentum_losses[momentum],
        f"Buy {direction} when price shows {momentum} momentum"
    )
    if p:
        patterns.append(p)

# ========================================
# FINAL REPORT
# ========================================
print("\n" + "="*80)
print("PATTERN DISCOVERY REPORT")
print("="*80)
print(f"Transaction Cost: {TX_COST*100}%")
print(f"Minimum Sample Size: {MIN_SAMPLE}")
print(f"Markets Analyzed: {len(valid_markets)}")
print(f"New Patterns Found: {len(patterns)}")
print("="*80)

if not patterns:
    print("\nNO NEW PROFITABLE PATTERNS FOUND")
    print("\nPossible reasons:")
    print("- Existing strategies already capture most edge")
    print("- Markets are efficient outside known biases")
    print("- Need more sophisticated pattern combinations")
else:
    # Sort by expected value
    patterns.sort(key=lambda x: x['expected_value'], reverse=True)
    
    for i, p in enumerate(patterns[:15], 1):  # Top 15
        print(f"\n#{i}. {p['pattern']}")
        print(f"    Description: {p['description']}")
        print(f"    Win Rate: {p['win_rate']*100:.2f}% ({p['wins']}W / {p['losses']}L)")
        print(f"    Sample Size: {p['sample_size']}")
        print(f"    Expected Value: {p['expected_value']*100:.2f}%")
        print(f"    Confidence: {p['confidence']}")
    
    if len(patterns) > 15:
        print(f"\n... and {len(patterns)-15} more patterns")

print("\n" + "="*80)
print("Analysis complete!")
