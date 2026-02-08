"""
Find LIVE markets that meet strategy conditions RIGHT NOW
These are real trading opportunities we can paper trade
"""
import json
import re

# Proven strategies
STRATEGIES = {
    'MUSK_FADE_EXTREMES': {
        'check': lambda q, prices: (
            bool(re.search(r'(\d+)-(\d+)\s+tweets', q, re.I)) and
            check_tweet_extreme(q)
        ),
        'expected_win': 97.1,
        'edge': 47.1
    },
    'WEATHER_FADE_LONGSHOTS': {
        'check': lambda q, prices: (
            bool(re.search(r'\btemperature\b|\bweather\b', q, re.I)) and
            get_latest_price(prices) < 0.30
        ),
        'expected_win': 93.9,
        'edge': 43.9
    },
    'ALTCOIN_FADE_HIGH': {
        'check': lambda q, prices: (
            bool(re.search(r'\bsolana\b|\bxrp\b|\bcardano\b', q, re.I)) and
            get_latest_price(prices) > 0.70
        ),
        'expected_win': 92.3,
        'edge': 42.3
    },
    'CRYPTO_FAVORITE_FADE': {
        'check': lambda q, prices: (
            bool(re.search(r'\bbitcoin\b.*\$\d+', q, re.I)) and
            get_latest_price(prices) > 0.70
        ),
        'expected_win': 61.9,
        'edge': 11.9
    }
}

def check_tweet_extreme(question):
    """Check if Musk tweet range is extreme (<40 or >200)"""
    match = re.search(r'(\d+)-(\d+)\s+tweets', question, re.I)
    if not match:
        return False
    
    low = int(match.group(1))
    high = int(match.group(2))
    
    return low < 40 or high > 200

def get_latest_price(prices):
    """Get most recent price from price history"""
    if not prices:
        return 0.5
    
    latest = prices[-1]
    
    if isinstance(latest, dict) and 'p' in latest:
        return latest['p']
    elif isinstance(latest, (int, float)):
        return latest
    
    return 0.5

def main():
    print("="*80)
    print("[LIVE OPPORTUNITIES] Real markets meeting strategy conditions NOW")
    print("="*80)
    
    print("\n[LOAD] 17K active markets...")
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        markets = json.load(f)
    
    print(f"[OK] {len(markets)} markets loaded\n")
    
    # Find opportunities for each strategy
    all_opportunities = []
    
    for strategy_name, params in STRATEGIES.items():
        print(f"{'='*80}")
        print(f"[STRATEGY] {strategy_name}")
        print(f"  Expected win rate: {params['expected_win']:.1f}%")
        print(f"  Expected edge: {params['edge']:.1f}%")
        print('='*80)
        
        opportunities = []
        
        for m in markets:
            question = m.get('question', '')
            prices = m.get('price_history', [])
            
            try:
                if params['check'](question, prices):
                    latest_price = get_latest_price(prices)
                    volume = m.get('volume', 0)
                    
                    opportunities.append({
                        'market_id': m.get('market_id'),
                        'question': question,
                        'price': latest_price,
                        'volume': volume,
                        'strategy': strategy_name,
                        'expected_win': params['expected_win'],
                        'edge': params['edge']
                    })
            except:
                pass
        
        print(f"\n[FOUND] {len(opportunities)} live opportunities")
        
        if opportunities:
            # Sort by volume (most liquid first)
            opportunities.sort(key=lambda o: o['volume'], reverse=True)
            
            print(f"\nTop 10 by volume:")
            for i, opp in enumerate(opportunities[:10], 1):
                print(f"\n  {i}. [{opp['strategy']}]")
                print(f"     {opp['question'][:70]}")
                print(f"     Volume: ${opp['volume']/1000:.0f}K")
                print(f"     Current price: {opp['price']:.3f}")
                print(f"     Expected win: {opp['expected_win']:.1f}%")
                print(f"     Edge: {opp['edge']:.1f}%")
            
            all_opportunities.extend(opportunities)
    
    # Overall summary
    print(f"\n{'='*80}")
    print(f"[OVERALL SUMMARY]")
    print('='*80)
    
    total_opps = len(all_opportunities)
    
    if total_opps == 0:
        print(f"\n  No live opportunities found")
        print(f"\n  This means:")
        print(f"    - No Musk extreme tweet markets active")
        print(f"    - No weather longshots (<30%) active")
        print(f"    - No altcoins >70% active")
        print(f"    - No BTC price targets >70% active")
        print(f"\n  Action: Monitor for new markets or wait for price movement")
    else:
        print(f"\n  Total opportunities: {total_opps}")
        
        # Breakdown by strategy
        from collections import Counter
        strategy_counts = Counter([o['strategy'] for o in all_opportunities])
        
        print(f"\n  By strategy:")
        for strategy, count in strategy_counts.most_common():
            print(f"    {strategy:30} {count:3} markets")
        
        # Top 5 overall (by expected win rate)
        all_opportunities.sort(key=lambda o: (o['expected_win'], o['volume']), reverse=True)
        
        print(f"\n  TOP 5 TRADES (highest win rate + volume):")
        for i, opp in enumerate(all_opportunities[:5], 1):
            print(f"\n    {i}. {opp['question'][:65]}")
            print(f"       Strategy: {opp['strategy']}")
            print(f"       Win: {opp['expected_win']:.1f}%, Edge: {opp['edge']:.1f}%")
            print(f"       Price: {opp['price']:.3f}, Volume: ${opp['volume']/1000:.0f}K")
        
        # Save to JSON for paper trading
        output_file = 'live_opportunities_snapshot.json'
        with open(output_file, 'w') as f:
            json.dump(all_opportunities, f, indent=2)
        
        print(f"\n[SAVED] {output_file}")
        print(f"  Use this for paper trading")

if __name__ == "__main__":
    main()
