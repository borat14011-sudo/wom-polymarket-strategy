#!/usr/bin/env python3
"""
REAL BACKTESTER #2: Category-Based Pattern Analysis
Analyzes 17,324 markets to find category-specific edges
"""

import json
import csv
import re
from collections import defaultdict
from datetime import datetime

# Category keywords for classification
CATEGORY_KEYWORDS = {
    'politics': [
        'trump', 'biden', 'election', 'president', 'congress', 'senate', 'house', 
        'democrat', 'republican', 'gop', 'vote', 'poll', 'governor', 'mayor',
        'cabinet', 'impeach', 'legislation', 'bill', 'law', 'supreme court',
        'musk', 'doge', 'epa', 'fda', 'sec', 'fed', 'treasury', 'tariff',
        'immigration', 'border', 'executive order', 'veto', 'pardon', 'political',
        'presidency', 'white house', 'congress', 'senator', 'representative'
    ],
    'crypto': [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol', 'doge',
        'dogecoin', 'altcoin', 'token', 'blockchain', 'defi', 'nft', 'usdt',
        'usdc', 'tether', 'binance', 'coinbase', 'ath', 'market cap', 'xrp',
        'cardano', 'ada', 'bnb', 'polygon', 'matic', 'avax', 'link', 'shiba',
        'pepe', 'memecoin', 'stablecoin', 'halving', 'etf', 'spot etf'
    ],
    'sports': [
        'nfl', 'nba', 'mlb', 'nhl', 'ufc', 'mma', 'boxing', 'tennis', 'golf',
        'super bowl', 'world series', 'stanley cup', 'championship', 'playoff',
        'mvp', 'coach', 'team', 'player', 'game', 'match', 'score', 'win',
        'soccer', 'football', 'basketball', 'baseball', 'hockey', 'f1', 'formula',
        'racing', 'olympics', 'medal', 'athlete', 'sport', 'league', 'season',
        'espn', 'draft', 'trade', 'free agent', 'premier league', 'champions league'
    ],
    'entertainment': [
        'movie', 'film', 'oscar', 'grammy', 'emmy', 'golden globe', 'award',
        'celebrity', 'actor', 'actress', 'singer', 'album', 'song', 'music',
        'netflix', 'disney', 'streaming', 'box office', 'tv show', 'series',
        'concert', 'tour', 'premiere', 'release', 'hollywood', 'drake', 'taylor',
        'kanye', 'beyonce', 'kardashian', 'tikto', 'influencer', 'youtube',
        'twitch', 'gaming', 'video game', 'esports', 'streamer'
    ],
    'weather': [
        'weather', 'temperature', 'rain', 'snow', 'storm', 'hurricane', 'tornado',
        'flood', 'drought', 'heat', 'cold', 'climate', 'forecast', 'celsius',
        'fahrenheit', 'wind', 'precipitation', 'humidity', 'sunny', 'cloudy',
        'el nino', 'la nina', 'noaa', 'wildfire', 'earthquake'
    ],
    'economics': [
        'gdp', 'inflation', 'cpi', 'unemployment', 'interest rate', 'federal reserve',
        'fed', 'rate cut', 'rate hike', 'recession', 'stock', 'market', 's&p',
        'nasdaq', 'dow', 'ipo', 'earnings', 'revenue', 'profit', 'economy',
        'trade', 'export', 'import', 'tariff', 'debt', 'deficit', 'bond',
        'yield', 'treasury', 'jobs report', 'payroll', 'gdp'
    ],
    'tech': [
        'ai', 'artificial intelligence', 'chatgpt', 'openai', 'google', 'apple',
        'microsoft', 'meta', 'facebook', 'amazon', 'nvidia', 'tesla', 'spacex',
        'rocket', 'launch', 'satellite', 'starlink', 'iphone', 'android',
        'app', 'software', 'hardware', 'chip', 'semiconductor', 'tech', 'startup',
        'ipo', 'merger', 'acquisition', 'antitrust', 'regulation', 'ceo'
    ],
    'geopolitics': [
        'war', 'russia', 'ukraine', 'china', 'taiwan', 'israel', 'gaza', 'iran',
        'north korea', 'nato', 'un', 'sanction', 'military', 'invasion', 'conflict',
        'peace', 'treaty', 'nuclear', 'missile', 'ceasefire', 'troops', 'attack',
        'terrorism', 'isis', 'taliban', 'coup', 'diplomatic', 'embassy'
    ],
    'social_media': [
        'tweet', 'twitter', 'x.com', 'post', 'follower', 'elon', 'musk tweet',
        'viral', 'trending', 'hashtag', 'retweet', 'likes', 'engagement',
        'instagram', 'threads', 'bluesky'
    ]
}

def categorize_market(question):
    """Categorize a market question into one or more categories"""
    question_lower = question.lower()
    matches = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in question_lower:
                matches.append(category)
                break
    
    if not matches:
        return ['other']
    return list(set(matches))

def load_backtest_data():
    """Load the main backtest dataset"""
    print("Loading backtest_dataset_v1.json (190MB)...")
    with open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json', 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} markets from backtest dataset")
    return data

def load_resolved_data():
    """Load resolved markets data"""
    resolved = {}
    
    # Load CSV resolved data (this has actual resolved markets)
    try:
        print("Loading polymarket_resolved_markets.csv...")
        with open(r'C:\Users\Borat\.openclaw\workspace\polymarket_resolved_markets.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_count = 0
            for row in reader:
                market_id = row.get('market_id') or row.get('id')
                if market_id:
                    # Parse winner field
                    winner = row.get('winner', '')
                    if winner:
                        row['outcome'] = winner
                    resolved[str(market_id)] = row
                    csv_count += 1
        print(f"Loaded {csv_count} resolved markets from CSV")
    except Exception as e:
        print(f"Error loading CSV: {e}")
    
    return resolved

def analyze_categories(markets, resolved):
    """Analyze each category for patterns and edges"""
    
    # Initialize category stats
    category_stats = defaultdict(lambda: {
        'total': 0,
        'resolved': 0,
        'favorites_total': 0,    # Markets where any price hit >70%
        'favorites_won': 0,      # Those that resolved YES
        'longshots_total': 0,    # Markets where price was <30%
        'longshots_won': 0,      # Those that resolved YES
        'price_movements': [],   # Track volatility
        'volumes': [],
        'questions': [],         # Sample questions
        'outcome_yes': 0,
        'outcome_no': 0,
        'final_prices': [],      # Final price before resolution
        'resolution_accuracy': [] # How close final price was to outcome
    })
    
    print("\nCategorizing and analyzing markets...")
    
    for market in markets:
        question = market.get('question', '')
        market_id = str(market.get('market_id', ''))
        categories = categorize_market(question)
        price_history = market.get('price_history', [])
        volume = market.get('volume', 0)
        outcome = market.get('outcome')
        is_closed = market.get('closed', False)
        
        # Get resolved data if available
        resolved_info = resolved.get(market_id, {})
        if not outcome and resolved_info:
            outcome = resolved_info.get('outcome') or resolved_info.get('result')
        
        # Calculate price statistics
        if price_history:
            prices = [p['p'] for p in price_history if 'p' in p]
            if prices:
                max_price = max(prices)
                min_price = min(prices)
                final_price = prices[-1]
                first_price = prices[0]
                volatility = max_price - min_price
                price_change = final_price - first_price
                
                for category in categories:
                    stats = category_stats[category]
                    stats['total'] += 1
                    stats['volumes'].append(volume)
                    stats['price_movements'].append({
                        'volatility': volatility,
                        'change': price_change,
                        'max': max_price,
                        'min': min_price,
                        'final': final_price
                    })
                    
                    if len(stats['questions']) < 5:
                        stats['questions'].append(question[:100])
                    
                    # Track favorites (price ever > 70%)
                    if max_price > 0.7:
                        stats['favorites_total'] += 1
                        if outcome == 'Yes' or outcome == True or outcome == 1 or outcome == '1':
                            stats['favorites_won'] += 1
                    
                    # Track longshots (final price < 30%)
                    if final_price < 0.3:
                        stats['longshots_total'] += 1
                        if outcome == 'Yes' or outcome == True or outcome == 1 or outcome == '1':
                            stats['longshots_won'] += 1
                    
                    # Track outcomes
                    if outcome:
                        stats['resolved'] += 1
                        stats['final_prices'].append(final_price)
                        
                        if outcome == 'Yes' or outcome == True or outcome == 1 or outcome == '1':
                            stats['outcome_yes'] += 1
                            # Resolution accuracy: how close was final price to 1?
                            stats['resolution_accuracy'].append(final_price)
                        elif outcome == 'No' or outcome == False or outcome == 0 or outcome == '0':
                            stats['outcome_no'] += 1
                            # Resolution accuracy: how close was final price to 0?
                            stats['resolution_accuracy'].append(1 - final_price)
    
    return category_stats

def calculate_edges(stats):
    """Calculate edge metrics for each category"""
    edges = {}
    
    for category, data in stats.items():
        if data['total'] < 10:
            continue
            
        # Favorite win rate
        fav_win_rate = data['favorites_won'] / data['favorites_total'] if data['favorites_total'] > 0 else 0
        
        # Longshot win rate
        longshot_win_rate = data['longshots_won'] / data['longshots_total'] if data['longshots_total'] > 0 else 0
        
        # Average volatility
        avg_volatility = sum(m['volatility'] for m in data['price_movements']) / len(data['price_movements']) if data['price_movements'] else 0
        
        # Average volume
        avg_volume = sum(data['volumes']) / len(data['volumes']) if data['volumes'] else 0
        
        # Yes bias
        yes_rate = data['outcome_yes'] / data['resolved'] if data['resolved'] > 0 else 0
        
        # Resolution accuracy
        avg_accuracy = sum(data['resolution_accuracy']) / len(data['resolution_accuracy']) if data['resolution_accuracy'] else 0
        
        # Calibration error (how far off predictions are)
        calibration_error = 0
        if data['final_prices'] and data['resolved'] > 0:
            # Perfect calibration: a market at 70% should resolve YES 70% of the time
            # We bucket by price ranges and check
            pass
        
        edges[category] = {
            'total_markets': data['total'],
            'resolved_markets': data['resolved'],
            'favorite_win_rate': fav_win_rate,
            'favorites_tested': data['favorites_total'],
            'longshot_win_rate': longshot_win_rate,
            'longshots_tested': data['longshots_total'],
            'avg_volatility': avg_volatility,
            'avg_volume': avg_volume,
            'yes_rate': yes_rate,
            'avg_accuracy': avg_accuracy,
            'sample_questions': data['questions'][:3],
            
            # Calculate potential edges
            'favorite_edge': fav_win_rate - 0.7 if data['favorites_total'] > 20 else None,  # vs implied 70%
            'longshot_edge': longshot_win_rate - 0.3 if data['longshots_total'] > 20 else None,  # vs implied 30%
        }
    
    return edges

def find_mispricing_patterns(stats):
    """Identify categories with consistent mispricing"""
    patterns = []
    
    for category, data in stats.items():
        if data['total'] < 50:
            continue
        
        # Pattern 1: Favorites underperform
        if data['favorites_total'] > 30:
            fav_rate = data['favorites_won'] / data['favorites_total']
            if fav_rate < 0.65:  # Favorites win less than 65%
                patterns.append({
                    'category': category,
                    'pattern': 'FAVORITES_OVERPRICED',
                    'detail': f'Favorites ({category}) win only {fav_rate:.1%} vs implied 70%+',
                    'strategy': f'FADE favorites in {category} markets',
                    'edge': (0.7 - fav_rate) * 100,
                    'sample_size': data['favorites_total']
                })
            elif fav_rate > 0.80:  # Favorites win more than 80%
                patterns.append({
                    'category': category,
                    'pattern': 'FAVORITES_UNDERPRICED',
                    'detail': f'Favorites ({category}) win {fav_rate:.1%} vs implied 70%',
                    'strategy': f'BUY favorites in {category} markets',
                    'edge': (fav_rate - 0.7) * 100,
                    'sample_size': data['favorites_total']
                })
        
        # Pattern 2: Longshots over/underperform
        if data['longshots_total'] > 30:
            long_rate = data['longshots_won'] / data['longshots_total']
            expected = 0.15  # <30% implies avg ~15% win rate
            if long_rate > 0.25:  # Longshots win more than 25%
                patterns.append({
                    'category': category,
                    'pattern': 'LONGSHOTS_UNDERPRICED',
                    'detail': f'Longshots ({category}) win {long_rate:.1%} vs expected ~15%',
                    'strategy': f'BUY longshots in {category} markets',
                    'edge': (long_rate - expected) * 100,
                    'sample_size': data['longshots_total']
                })
            elif long_rate < 0.08:  # Longshots win less than 8%
                patterns.append({
                    'category': category,
                    'pattern': 'LONGSHOTS_OVERPRICED',
                    'detail': f'Longshots ({category}) win only {long_rate:.1%}',
                    'strategy': f'FADE (sell) longshots in {category} markets',
                    'edge': (expected - long_rate) * 100,
                    'sample_size': data['longshots_total']
                })
        
        # Pattern 3: High volatility (overreaction)
        movements = data['price_movements']
        if len(movements) > 50:
            avg_vol = sum(m['volatility'] for m in movements) / len(movements)
            if avg_vol > 0.4:  # Price swings > 40%
                patterns.append({
                    'category': category,
                    'pattern': 'HIGH_VOLATILITY',
                    'detail': f'{category} markets have avg {avg_vol:.1%} price swings',
                    'strategy': f'Mean reversion plays in {category} after big moves',
                    'edge': 'Qualitative - volatility arbitrage',
                    'sample_size': len(movements)
                })
    
    return sorted(patterns, key=lambda x: x.get('edge', 0) if isinstance(x.get('edge'), (int, float)) else 0, reverse=True)

def generate_report(stats, edges, patterns):
    """Generate markdown report"""
    
    report = """# 🎯 Category-Based Backtest Analysis
## Real Historical Data from 17,324 Polymarket Markets

Generated: {date}

---

## 📊 Category Breakdown

| Category | Total Markets | Resolved | Avg Volume | Volatility |
|----------|--------------|----------|------------|------------|
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    # Sort by total markets
    sorted_cats = sorted(edges.items(), key=lambda x: x[1]['total_markets'], reverse=True)
    
    for category, data in sorted_cats:
        report += f"| {category.upper()} | {data['total_markets']:,} | {data['resolved_markets']:,} | ${data['avg_volume']:,.0f} | {data['avg_volatility']:.1%} |\n"
    
    report += "\n---\n\n## 🏆 Favorite Performance by Category\n\n"
    report += "Favorites = markets where price exceeded 70% at some point\n\n"
    report += "| Category | Favorites Tested | Win Rate | Expected | Edge |\n"
    report += "|----------|-----------------|----------|----------|------|\n"
    
    for category, data in sorted_cats:
        if data['favorites_tested'] > 20:
            edge = data.get('favorite_edge')
            edge_str = f"{edge:+.1%}" if edge else "N/A"
            report += f"| {category.upper()} | {data['favorites_tested']:,} | {data['favorite_win_rate']:.1%} | 70%+ | {edge_str} |\n"
    
    report += "\n---\n\n## 🎰 Longshot Performance by Category\n\n"
    report += "Longshots = markets trading below 30% at final price\n\n"
    report += "| Category | Longshots Tested | Win Rate | Expected | Edge |\n"
    report += "|----------|-----------------|----------|----------|------|\n"
    
    for category, data in sorted_cats:
        if data['longshots_tested'] > 20:
            edge = data.get('longshot_edge')
            edge_str = f"{edge:+.1%}" if edge else "N/A"
            report += f"| {category.upper()} | {data['longshots_tested']:,} | {data['longshot_win_rate']:.1%} | ~15% | {edge_str} |\n"
    
    report += "\n---\n\n## ⚠️ Mispricing Patterns Discovered\n\n"
    
    if patterns:
        for i, p in enumerate(patterns[:10], 1):
            edge_str = f"{p['edge']:.1f}%" if isinstance(p['edge'], (int, float)) else p['edge']
            report += f"""### {i}. {p['pattern']} - {p['category'].upper()}

**Finding:** {p['detail']}

**Strategy:** {p['strategy']}

**Edge:** {edge_str} | Sample Size: {p['sample_size']} markets

---

"""
    else:
        report += "No significant mispricing patterns found with current sample sizes.\n\n"
    
    report += "## 🥇 TOP 3 CATEGORY-BASED STRATEGIES\n\n"
    
    # Generate top strategies
    strategies = []
    
    for category, data in sorted_cats:
        if data['favorites_tested'] > 30:
            fav_edge = data.get('favorite_edge', 0) or 0
            if abs(fav_edge) > 0.05:  # 5% edge
                direction = "BUY" if fav_edge > 0 else "FADE"
                strategies.append({
                    'strategy': f'{direction} favorites in {category.upper()}',
                    'edge': abs(fav_edge),
                    'sample': data['favorites_tested'],
                    'detail': f"Win rate {data['favorite_win_rate']:.1%} vs 70% implied"
                })
        
        if data['longshots_tested'] > 30:
            long_edge = data.get('longshot_edge', 0) or 0
            if abs(long_edge) > 0.05:
                direction = "BUY" if long_edge > 0 else "FADE"
                strategies.append({
                    'strategy': f'{direction} longshots in {category.upper()}',
                    'edge': abs(long_edge),
                    'sample': data['longshots_tested'],
                    'detail': f"Win rate {data['longshot_win_rate']:.1%} vs ~15% expected"
                })
    
    strategies.sort(key=lambda x: x['edge'], reverse=True)
    
    for i, s in enumerate(strategies[:3], 1):
        report += f"""### Strategy #{i}: {s['strategy']}

- **Edge:** {s['edge']:.1%}
- **Sample Size:** {s['sample']} markets
- **Details:** {s['detail']}

"""
    
    if not strategies:
        report += """
Based on current data, no strategies with >5% edge detected. This could mean:
1. Markets are well-calibrated
2. Need more resolved market data
3. Edge exists in other dimensions (timing, volume, etc.)

"""
    
    report += """---

## 📈 Key Insights

### By Category:

"""
    
    for category, data in sorted_cats[:5]:
        report += f"""**{category.upper()}:**
- {data['total_markets']:,} total markets analyzed
- Favorites win {data['favorite_win_rate']:.1%} of the time (n={data['favorites_tested']})
- Longshots win {data['longshot_win_rate']:.1%} of the time (n={data['longshots_tested']})
- Average volatility: {data['avg_volatility']:.1%}
- Sample questions: {data['sample_questions'][0] if data['sample_questions'] else 'N/A'}

"""
    
    report += """
---

## 🔬 Methodology

1. **Data Source:** backtest_dataset_v1.json (17,324 markets with price histories)
2. **Categorization:** Keyword matching across 9 categories + "other"
3. **Favorite Definition:** Max price ever > 70%
4. **Longshot Definition:** Final price < 30%
5. **Edge Calculation:** Actual win rate - implied probability

## ⚠️ Limitations

- Many markets not yet resolved (outcome = null)
- Categories may overlap (e.g., "Trump crypto" = politics + crypto)
- Historical data doesn't guarantee future patterns
- Sample sizes vary significantly by category

"""
    
    return report

def main():
    print("=" * 60)
    print("REAL BACKTESTER #2: Category-Based Analysis")
    print("=" * 60)
    
    # Load data
    markets = load_backtest_data()
    resolved = load_resolved_data()
    
    print(f"\nTotal markets: {len(markets)}")
    print(f"Resolved data entries: {len(resolved)}")
    
    # Analyze categories
    stats = analyze_categories(markets, resolved)
    
    # Calculate edges
    edges = calculate_edges(stats)
    
    # Find mispricing patterns
    patterns = find_mispricing_patterns(stats)
    
    # Generate report
    report = generate_report(stats, edges, patterns)
    
    # Save report
    output_path = r'C:\Users\Borat\.openclaw\workspace\real_backtest_categories.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[OK] Report saved to: {output_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\nCategories analyzed: {len(edges)}")
    print(f"Mispricing patterns found: {len(patterns)}")
    
    if patterns:
        print("\nTop patterns:")
        for p in patterns[:3]:
            print(f"  - {p['category'].upper()}: {p['pattern']}")
    
    print("\nCategory breakdown:")
    for cat, data in sorted(edges.items(), key=lambda x: x[1]['total_markets'], reverse=True)[:5]:
        print(f"  {cat}: {data['total_markets']:,} markets, {data['resolved_markets']:,} resolved")

if __name__ == '__main__':
    main()
