#!/usr/bin/env python3
"""
Backtest Pattern Analysis - Statistical Deep Dive
"""
import json
import statistics
from datetime import datetime
from collections import defaultdict, Counter
import re

def parse_timestamp(ts):
    """Convert unix timestamp to datetime"""
    return datetime.fromtimestamp(ts)

def categorize_market(question):
    """Categorize market by question content"""
    q_lower = question.lower()
    
    # Sports keywords
    sports_keywords = ['nfl', 'nba', 'mlb', 'nhl', 'ufc', 'soccer', 'football', 'basketball', 
                       'baseball', 'hockey', 'game', 'championship', 'super bowl', 'world series',
                       'playoffs', 'finals', 'match', 'team', 'player stats']
    
    # Politics keywords
    politics_keywords = ['trump', 'biden', 'election', 'president', 'congress', 'senate', 
                         'house', 'political', 'vote', 'governor', 'democrat', 'republican',
                         'poll', 'approval', 'legislation', 'bill', 'supreme court']
    
    # Crypto keywords
    crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
                       'solana', 'sol', 'dogecoin', 'blockchain', 'defi', 'nft']
    
    # Weather keywords
    weather_keywords = ['temperature', 'weather', 'snow', 'rain', 'hurricane', 'storm',
                        'forecast', 'climate', 'degrees', 'celsius', 'fahrenheit']
    
    # Elon/Twitter/Social
    social_keywords = ['elon musk', 'tweet', 'twitter', 'x.com', 'post', 'social media']
    
    for keyword in sports_keywords:
        if keyword in q_lower:
            return 'sports'
    
    for keyword in politics_keywords:
        if keyword in q_lower:
            return 'politics'
    
    for keyword in crypto_keywords:
        if keyword in q_lower:
            return 'crypto'
    
    for keyword in weather_keywords:
        if keyword in q_lower:
            return 'weather'
    
    for keyword in social_keywords:
        if keyword in q_lower:
            return 'social_media'
    
    return 'other'

def extract_price_patterns(price_history):
    """Extract trading patterns from price history"""
    if not price_history or len(price_history) < 2:
        return {}
    
    prices = [p['p'] for p in price_history]
    
    # Price movement patterns
    initial_price = prices[0]
    final_price = prices[-1]
    max_price = max(prices)
    min_price = min(prices)
    
    # Volatility
    price_changes = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    avg_volatility = statistics.mean(price_changes) if price_changes else 0
    
    # Trend detection
    if len(prices) >= 3:
        early_avg = statistics.mean(prices[:len(prices)//3])
        late_avg = statistics.mean(prices[-len(prices)//3:])
        trend = 'upward' if late_avg > early_avg * 1.1 else ('downward' if late_avg < early_avg * 0.9 else 'stable')
    else:
        trend = 'unknown'
    
    # Price range
    if initial_price < 0.1:
        price_tier = 'extreme_underdog'  # < 10%
    elif initial_price < 0.3:
        price_tier = 'underdog'  # 10-30%
    elif initial_price < 0.7:
        price_tier = 'competitive'  # 30-70%
    elif initial_price < 0.9:
        price_tier = 'favorite'  # 70-90%
    else:
        price_tier = 'extreme_favorite'  # > 90%
    
    return {
        'initial_price': initial_price,
        'final_price': final_price,
        'max_price': max_price,
        'min_price': min_price,
        'price_range': max_price - min_price,
        'volatility': avg_volatility,
        'trend': trend,
        'price_tier': price_tier,
        'total_ticks': len(price_history)
    }

def analyze_entry_timing(price_history, outcome):
    """Analyze correlation between entry timing and success"""
    if not price_history or outcome is None:
        return None
    
    market_duration = price_history[-1]['t'] - price_history[0]['t']
    
    # Simulate entries at different points
    results = []
    for i in range(0, len(price_history), max(1, len(price_history)//10)):
        entry_time = price_history[i]['t']
        entry_price = price_history[i]['p']
        
        time_into_market = (entry_time - price_history[0]['t']) / market_duration if market_duration > 0 else 0
        
        # Calculate profit if took YES position
        profit = (1.0 - entry_price) if outcome == 'yes' else -entry_price
        
        results.append({
            'entry_pct': time_into_market,
            'entry_price': entry_price,
            'profit': profit
        })
    
    return results

def main():
    print("=" * 80)
    print("POLYMARKET BACKTEST ANALYSIS - PATTERN DISCOVERY")
    print("=" * 80)
    print()
    
    # Load data
    with open('polymarket-monitor/historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    
    print(f"📊 Total Markets: {len(data)}\n")
    
    # Filter for closed markets with outcomes
    closed_markets = [m for m in data if m.get('closed') and m.get('outcome')]
    print(f"✅ Closed Markets with Outcomes: {len(closed_markets)}")
    print(f"❌ Open/No Outcome: {len(data) - len(closed_markets)}\n")
    
    if len(closed_markets) < 30:
        print("⚠️  WARNING: Less than 30 closed markets. Analysis will be statistically weak.")
        print()
    
    # === CATEGORY ANALYSIS ===
    print("=" * 80)
    print("1. WIN RATE BY MARKET CATEGORY")
    print("=" * 80)
    
    category_stats = defaultdict(lambda: {'total': 0, 'yes': 0, 'no': 0, 'volumes': [], 'questions': []})
    
    for market in closed_markets:
        category = categorize_market(market['question'])
        outcome = market['outcome'].lower()
        volume = market.get('volume', 0)
        
        category_stats[category]['total'] += 1
        category_stats[category][outcome] += 1
        category_stats[category]['volumes'].append(volume)
        if len(category_stats[category]['questions']) < 3:  # Sample questions
            category_stats[category]['questions'].append(market['question'][:80])
    
    for category in sorted(category_stats.keys(), key=lambda x: category_stats[x]['total'], reverse=True):
        stats = category_stats[category]
        total = stats['total']
        
        if total < 5:
            sig = "⚠️  LOW SAMPLE"
        elif total < 30:
            sig = "⚠️  WEAK"
        else:
            sig = "✅ STRONG"
        
        yes_rate = stats['yes'] / total * 100 if total > 0 else 0
        avg_volume = statistics.mean(stats['volumes']) if stats['volumes'] else 0
        
        print(f"\n{category.upper()}: {sig}")
        print(f"  Sample Size: {total} markets")
        print(f"  YES outcomes: {stats['yes']} ({yes_rate:.1f}%)")
        print(f"  NO outcomes: {stats['no']} ({100-yes_rate:.1f}%)")
        print(f"  Avg Volume: ${avg_volume:,.0f}")
        print(f"  Sample questions:")
        for q in stats['questions'][:2]:
            print(f"    - {q}...")
    
    # === PRICE TIER PATTERNS ===
    print("\n" + "=" * 80)
    print("2. TRADING PATTERNS BY PRICE TIER")
    print("=" * 80)
    
    tier_stats = defaultdict(lambda: {'total': 0, 'yes': 0, 'no': 0, 'profits': []})
    
    for market in closed_markets:
        if not market.get('price_history'):
            continue
        
        patterns = extract_price_patterns(market['price_history'])
        tier = patterns.get('price_tier')
        outcome = market['outcome'].lower()
        
        if tier:
            tier_stats[tier]['total'] += 1
            tier_stats[tier][outcome] += 1
            
            # Calculate hypothetical profit (buying YES at initial price)
            initial = patterns['initial_price']
            profit = (1.0 - initial) if outcome == 'yes' else -initial
            tier_stats[tier]['profits'].append(profit)
    
    tier_order = ['extreme_underdog', 'underdog', 'competitive', 'favorite', 'extreme_favorite']
    
    for tier in tier_order:
        if tier not in tier_stats:
            continue
        
        stats = tier_stats[tier]
        total = stats['total']
        
        if total < 30:
            sig = "⚠️  WEAK" if total >= 5 else "⚠️  LOW SAMPLE"
        else:
            sig = "✅ STRONG"
        
        yes_rate = stats['yes'] / total * 100 if total > 0 else 0
        avg_profit = statistics.mean(stats['profits']) if stats['profits'] else 0
        
        print(f"\n{tier.replace('_', ' ').upper()}: {sig}")
        print(f"  Sample Size: {total} markets")
        print(f"  YES rate: {yes_rate:.1f}%")
        print(f"  Avg ROI (YES bet): {avg_profit*100:.1f}%")
        print(f"  Total ROI: {sum(stats['profits'])*100:.1f}%")
    
    # === TREND PATTERNS ===
    print("\n" + "=" * 80)
    print("3. TREND-BASED PATTERNS (NEW DISCOVERY)")
    print("=" * 80)
    
    trend_stats = defaultdict(lambda: {'total': 0, 'yes': 0, 'no': 0, 'profits': []})
    
    for market in closed_markets:
        if not market.get('price_history') or len(market.get('price_history', [])) < 5:
            continue
        
        patterns = extract_price_patterns(market['price_history'])
        trend = patterns.get('trend')
        outcome = market['outcome'].lower()
        
        if trend and trend != 'unknown':
            trend_stats[trend]['total'] += 1
            trend_stats[trend][outcome] += 1
            
            profit = (1.0 - patterns['initial_price']) if outcome == 'yes' else -patterns['initial_price']
            trend_stats[trend]['profits'].append(profit)
    
    for trend in ['upward', 'stable', 'downward']:
        if trend not in trend_stats:
            continue
        
        stats = trend_stats[trend]
        total = stats['total']
        
        if total < 30:
            sig = "⚠️  WEAK" if total >= 5 else "⚠️  LOW SAMPLE"
        else:
            sig = "✅ STRONG"
        
        yes_rate = stats['yes'] / total * 100 if total > 0 else 0
        avg_profit = statistics.mean(stats['profits']) if stats['profits'] else 0
        
        print(f"\n{trend.upper()} TREND: {sig}")
        print(f"  Sample Size: {total} markets")
        print(f"  YES rate: {yes_rate:.1f}%")
        print(f"  Avg ROI: {avg_profit*100:.1f}%")
    
    # === VOLATILITY PATTERNS ===
    print("\n" + "=" * 80)
    print("4. VOLATILITY-BASED PATTERNS (NEW DISCOVERY)")
    print("=" * 80)
    
    volatility_buckets = {'low': [], 'medium': [], 'high': []}
    
    for market in closed_markets:
        if not market.get('price_history') or len(market.get('price_history', [])) < 3:
            continue
        
        patterns = extract_price_patterns(market['price_history'])
        vol = patterns.get('volatility', 0)
        outcome = market['outcome'].lower()
        
        profit = (1.0 - patterns['initial_price']) if outcome == 'yes' else -patterns['initial_price']
        
        if vol < 0.01:
            bucket = 'low'
        elif vol < 0.05:
            bucket = 'medium'
        else:
            bucket = 'high'
        
        volatility_buckets[bucket].append({
            'outcome': outcome,
            'profit': profit,
            'vol': vol
        })
    
    for bucket in ['low', 'medium', 'high']:
        trades = volatility_buckets[bucket]
        if not trades:
            continue
        
        total = len(trades)
        yes_count = sum(1 for t in trades if t['outcome'] == 'yes')
        yes_rate = yes_count / total * 100
        avg_profit = statistics.mean([t['profit'] for t in trades])
        
        sig = "✅ STRONG" if total >= 30 else ("⚠️  WEAK" if total >= 5 else "⚠️  LOW SAMPLE")
        
        print(f"\n{bucket.upper()} VOLATILITY: {sig}")
        print(f"  Sample Size: {total} markets")
        print(f"  YES rate: {yes_rate:.1f}%")
        print(f"  Avg ROI: {avg_profit*100:.1f}%")
    
    # === EDGE DECAY ANALYSIS ===
    print("\n" + "=" * 80)
    print("5. EDGE DECAY OVER TIME")
    print("=" * 80)
    
    # Group by time periods
    time_buckets = defaultdict(list)
    
    for market in closed_markets:
        if not market.get('start_date'):
            continue
        
        try:
            start_dt = datetime.fromisoformat(market['start_date'].replace('Z', '+00:00'))
            month_key = start_dt.strftime('%Y-%m')
            
            patterns = extract_price_patterns(market.get('price_history', []))
            outcome = market['outcome'].lower()
            
            if patterns:
                profit = (1.0 - patterns['initial_price']) if outcome == 'yes' else -patterns['initial_price']
                time_buckets[month_key].append(profit)
        except:
            continue
    
    print(f"\nMonthly Performance (YES strategy):")
    for month in sorted(time_buckets.keys()):
        profits = time_buckets[month]
        if len(profits) < 5:
            continue
        
        avg_roi = statistics.mean(profits) * 100
        total_roi = sum(profits) * 100
        count = len(profits)
        
        print(f"  {month}: {count} trades, Avg ROI: {avg_roi:+.1f}%, Total: {total_roi:+.1f}%")
    
    # === ENTRY TIMING ANALYSIS ===
    print("\n" + "=" * 80)
    print("6. ENTRY TIMING CORRELATION")
    print("=" * 80)
    
    timing_buckets = defaultdict(list)
    
    for market in closed_markets:
        if not market.get('price_history') or market.get('outcome') is None:
            continue
        
        outcome = 'yes' if market['outcome'].lower() == 'yes' else 'no'
        timing_data = analyze_entry_timing(market['price_history'], outcome)
        
        if timing_data:
            for entry in timing_data:
                pct = entry['entry_pct']
                bucket = int(pct * 10) * 10  # 0%, 10%, 20%, etc.
                timing_buckets[bucket].append(entry['profit'])
    
    print("\nProfit by Entry Time (% into market lifecycle):")
    for bucket in sorted(timing_buckets.keys()):
        profits = timing_buckets[bucket]
        if len(profits) < 10:
            continue
        
        avg_roi = statistics.mean(profits) * 100
        count = len(profits)
        sig = "✅" if count >= 30 else "⚠️ "
        
        print(f"  {bucket:3d}%-{bucket+9:3d}%: {sig} {count:4d} entries, Avg ROI: {avg_roi:+.1f}%")
    
    # === POSITION SIZING ===
    print("\n" + "=" * 80)
    print("7. POSITION SIZING INSIGHTS")
    print("=" * 80)
    
    volume_buckets = {'micro': [], 'small': [], 'medium': [], 'large': [], 'mega': []}
    
    for market in closed_markets:
        volume = market.get('volume', 0)
        outcome = market['outcome'].lower()
        
        patterns = extract_price_patterns(market.get('price_history', []))
        if not patterns:
            continue
        
        profit = (1.0 - patterns['initial_price']) if outcome == 'yes' else -patterns['initial_price']
        
        if volume < 10000:
            bucket = 'micro'
        elif volume < 50000:
            bucket = 'small'
        elif volume < 200000:
            bucket = 'medium'
        elif volume < 1000000:
            bucket = 'large'
        else:
            bucket = 'mega'
        
        volume_buckets[bucket].append({
            'volume': volume,
            'profit': profit,
            'outcome': outcome
        })
    
    print("\nPerformance by Market Volume:")
    for bucket in ['micro', 'small', 'medium', 'large', 'mega']:
        trades = volume_buckets[bucket]
        if not trades:
            continue
        
        total = len(trades)
        yes_count = sum(1 for t in trades if t['outcome'] == 'yes')
        yes_rate = yes_count / total * 100
        avg_profit = statistics.mean([t['profit'] for t in trades])
        avg_volume = statistics.mean([t['volume'] for t in trades])
        
        sig = "✅ STRONG" if total >= 30 else ("⚠️  WEAK" if total >= 5 else "⚠️  LOW SAMPLE")
        
        print(f"\n{bucket.upper()}: {sig}")
        print(f"  Sample Size: {total} markets")
        print(f"  Avg Volume: ${avg_volume:,.0f}")
        print(f"  YES rate: {yes_rate:.1f}%")
        print(f"  Avg ROI: {avg_profit*100:.1f}%")
    
    # === SUMMARY ===
    print("\n" + "=" * 80)
    print("STATISTICAL SIGNIFICANCE SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal analyzed: {len(closed_markets)} closed markets")
    print(f"Minimum threshold for significance: 30 trades")
    print(f"\nCategories with STRONG significance (≥30 trades):")
    
    strong_patterns = []
    for category, stats in category_stats.items():
        if stats['total'] >= 30:
            strong_patterns.append(f"  - {category}: {stats['total']} trades")
    
    for tier, stats in tier_stats.items():
        if stats['total'] >= 30:
            strong_patterns.append(f"  - {tier} price tier: {stats['total']} trades")
    
    for trend, stats in trend_stats.items():
        if stats['total'] >= 30:
            strong_patterns.append(f"  - {trend} trend: {stats['total']} trades")
    
    if strong_patterns:
        for pattern in strong_patterns:
            print(pattern)
    else:
        print("  ⚠️  NONE - All patterns are below statistical significance threshold")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
