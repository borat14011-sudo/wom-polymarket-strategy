#!/usr/bin/env python3
"""
MARKET COMPOSITION ANALYZER
Analyzes current market landscape to identify pattern opportunities
"""
import requests
import json
from datetime import datetime
from collections import Counter

GAMMA_API = "https://gamma-api.polymarket.com"

def fetch_all_active_markets(limit=200):
    """Fetch all active markets"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    all_markets = []
    offset = 0
    
    while len(all_markets) < limit:
        try:
            url = f"{GAMMA_API}/markets"
            params = {
                'closed': 'false',
                'limit': 100,
                'offset': offset,
                '_sort': 'volume24hr',
                '_order': 'DESC'
            }
            
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            markets = response.json()
            if not markets:
                break
                
            all_markets.extend(markets)
            offset += len(markets)
            
            if len(markets) < 100:
                break
                
        except Exception as e:
            print(f"Error: {e}")
            break
    
    return all_markets[:limit]

def analyze_market_composition(markets):
    """Analyze what types of markets are available"""
    
    # Category counters
    categories = {
        'Crypto': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol'],
        'Political': ['trump', 'biden', 'election', 'senate', 'house', 'congress', 'vote'],
        'Sports': ['nba', 'nfl', 'super bowl', 'points', 'yards', 'touchdown'],
        'Elon/Musk': ['elon', 'musk', 'tweet', 'doge'],
        'Weather': ['temperature', 'snow', 'rain', 'storm'],
        'Entertainment': ['grammy', 'oscar', 'album', 'taylor swift', 'movie'],
        'Economic': ['inflation', 'fed', 'jobs', 'unemployment', 'gdp'],
        'Tech': ['apple', 'ai', 'gpt', 'google', 'meta'],
        'Other': []
    }
    
    # Price distribution
    price_ranges = {
        '0-10%': 0,
        '10-25%': 0,
        '25-40%': 0,
        '40-60%': 0,
        '60-75%': 0,
        '75-90%': 0,
        '90-100%': 0
    }
    
    # Volume distribution
    volume_ranges = {
        '0-10K': 0,
        '10K-100K': 0,
        '100K-1M': 0,
        '1M+': 0
    }
    
    category_counts = {k: 0 for k in categories.keys()}
    high_confidence_markets = []
    low_confidence_markets = []
    
    for market in markets:
        question = market.get('question', '').lower()
        
        # Get price
        try:
            outcome_prices = market.get('outcomePrices', [0.5, 0.5])
            yes_price = float(outcome_prices[0]) if isinstance(outcome_prices[0], str) else 0.5
        except:
            yes_price = 0.5
        
        # Get volume
        try:
            volume = float(market.get('volume', 0))
        except:
            volume = 0
        
        # Categorize
        matched = False
        for cat_name, keywords in categories.items():
            if cat_name == 'Other':
                continue
            if any(kw in question for kw in keywords):
                category_counts[cat_name] += 1
                matched = True
                break
        
        if not matched:
            category_counts['Other'] += 1
        
        # Price distribution
        if yes_price < 0.10:
            price_ranges['0-10%'] += 1
        elif yes_price < 0.25:
            price_ranges['10-25%'] += 1
        elif yes_price < 0.40:
            price_ranges['25-40%'] += 1
        elif yes_price < 0.60:
            price_ranges['40-60%'] += 1
        elif yes_price < 0.75:
            price_ranges['60-75%'] += 1
        elif yes_price < 0.90:
            price_ranges['75-90%'] += 1
        else:
            price_ranges['90-100%'] += 1
        
        # Volume distribution
        if volume < 10000:
            volume_ranges['0-10K'] += 1
        elif volume < 100000:
            volume_ranges['10K-100K'] += 1
        elif volume < 1000000:
            volume_ranges['100K-1M'] += 1
        else:
            volume_ranges['1M+'] += 1
        
        # High confidence (>90%) - potential fade opportunities
        if yes_price > 0.90:
            high_confidence_markets.append({
                'question': market.get('question'),
                'yes_price': yes_price,
                'volume': volume
            })
        
        # Low confidence (<15%) - potential value opportunities
        if yes_price < 0.15:
            low_confidence_markets.append({
                'question': market.get('question'),
                'yes_price': yes_price,
                'volume': volume
            })
    
    return {
        'category_counts': category_counts,
        'price_ranges': price_ranges,
        'volume_ranges': volume_ranges,
        'high_confidence': high_confidence_markets,
        'low_confidence': low_confidence_markets
    }

def generate_report(analysis, total_markets):
    """Generate analysis report"""
    lines = []
    lines.append("=" * 80)
    lines.append("POLYMARKET COMPOSITION ANALYSIS")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Markets Analyzed: {total_markets}")
    lines.append("=" * 80)
    
    # Categories
    lines.append("\n### MARKET CATEGORIES")
    lines.append("-" * 40)
    for cat, count in sorted(analysis['category_counts'].items(), key=lambda x: x[1], reverse=True):
        pct = count / total_markets * 100 if total_markets > 0 else 0
        lines.append(f"  {cat:15} {count:4} markets ({pct:5.1f}%)")
    
    # Price distribution
    lines.append("\n### PRICE DISTRIBUTION (YES)")
    lines.append("-" * 40)
    for range_name, count in analysis['price_ranges'].items():
        pct = count / total_markets * 100 if total_markets > 0 else 0
        bar = "#" * int(pct / 2)
        lines.append(f"  {range_name:10} {count:4} ({pct:5.1f}%) {bar}")
    
    # Volume distribution
    lines.append("\n### VOLUME DISTRIBUTION")
    lines.append("-" * 40)
    for range_name, count in analysis['volume_ranges'].items():
        pct = count / total_markets * 100 if total_markets > 0 else 0
        lines.append(f"  {range_name:10} {count:4} markets ({pct:5.1f}%)")
    
    # High confidence markets (fade opportunities)
    lines.append("\n### HIGH CONFIDENCE MARKETS (>90% YES) - FADE CANDIDATES")
    lines.append("-" * 40)
    if analysis['high_confidence']:
        for m in sorted(analysis['high_confidence'], key=lambda x: x['yes_price'], reverse=True)[:10]:
            lines.append(f"  {m['yes_price']:.1%} - {m['question'][:60]}")
            lines.append(f"           Volume: ${m['volume']:,.0f}")
    else:
        lines.append("  No markets above 90% confidence")
    
    # Low confidence markets (value opportunities)
    lines.append("\n### LOW CONFIDENCE MARKETS (<15% YES) - VALUE CANDIDATES")
    lines.append("-" * 40)
    if analysis['low_confidence']:
        for m in sorted(analysis['low_confidence'], key=lambda x: x['yes_price'])[:10]:
            lines.append(f"  {m['yes_price']:.1%} - {m['question'][:60]}")
            lines.append(f"           Volume: ${m['volume']:,.0f}")
    else:
        lines.append("  No markets below 15% confidence")
    
    # Pattern opportunities
    lines.append("\n### POTENTIAL PATTERN OPPORTUNITIES")
    lines.append("-" * 40)
    
    high_conf_count = len(analysis['high_confidence'])
    low_conf_count = len(analysis['low_confidence'])
    
    if high_conf_count > 5:
        lines.append(f"  [STRONG] High confidence fade: {high_conf_count} markets >90%")
        lines.append("           Consider: Bet NO on extreme confidence")
    
    if low_conf_count > 5:
        lines.append(f"  [STRONG] Low confidence value: {low_conf_count} markets <15%")
        lines.append("           Consider: Bet YES on oversold markets")
    
    lines.append("\n  [MEDIUM] Category concentrations detected")
    top_cat = max(analysis['category_counts'].items(), key=lambda x: x[1])
    lines.append(f"           {top_cat[0]} dominates with {top_cat[1]} markets")
    
    lines.append("\n" + "=" * 80)
    return "\n".join(lines)

def main():
    print("Fetching market data...")
    markets = fetch_all_active_markets(limit=200)
    
    if not markets:
        print("No markets fetched!")
        return
    
    print(f"Analyzing {len(markets)} markets...")
    analysis = analyze_market_composition(markets)
    
    report = generate_report(analysis, len(markets))
    print(report)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    with open(f'market_composition_{timestamp}.json', 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'markets_analyzed': len(markets),
            'analysis': analysis
        }, f, indent=2)
    
    with open(f'market_composition_{timestamp}.txt', 'w') as f:
        f.write(report)
    
    print(f"\n[DONE] Saved to market_composition_{timestamp}.json/txt")

if __name__ == "__main__":
    main()
