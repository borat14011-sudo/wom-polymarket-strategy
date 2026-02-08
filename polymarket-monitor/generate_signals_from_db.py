"""
Generate trading signals from categorized database
Applies event-driven strategies to find opportunities
"""
import sqlite3
import re
from datetime import datetime

# Strategy parameters (from event backtest)
STRATEGIES = {
    'ALTCOIN_FADE_HIGH': {
        'category': 'Crypto/Altcoins',
        'condition': 'initial_price > 0.70',
        'direction': 'NO',
        'win_rate': 0.923,
        'edge': 0.423,
        'description': 'Short altcoin markets starting above 70%'
    },
    'CRYPTO_FAVORITE_FADE': {
        'category': 'Crypto/BTC-Price',
        'condition': 'initial_price > 0.70',
        'direction': 'NO',
        'win_rate': 0.619,
        'edge': 0.119,
        'description': 'Short high-conviction BTC price predictions'
    }
}

def extract_initial_price_proxy(question: str) -> float:
    """
    Estimate initial price from question wording
    High price targets = high initial price
    """
    question_lower = question.lower()
    
    # Look for price targets
    btc_match = re.search(r'\$(\d+),?(\d+)', question)
    if btc_match:
        price = int(btc_match.group(1) + (btc_match.group(2) if btc_match.group(2) else ''))
        # Current BTC ~$100K, so $150K+ = high confidence = >0.70 initial
        if price >= 150000:
            return 0.75
        elif price >= 120000:
            return 0.60
        else:
            return 0.40
    
    # Altcoins with very high targets
    sol_match = re.search(r'solana.*\$(\d+)', question_lower)
    if sol_match:
        price = int(sol_match.group(1))
        if price >= 500:  # SOL $500+ is very bullish
            return 0.75
        elif price >= 300:
            return 0.60
        else:
            return 0.45
    
    xrp_match = re.search(r'xrp.*\$(\d+)', question_lower)
    if xrp_match:
        price = int(xrp_match.group(1))
        if price >= 10:  # XRP $10+ is very bullish
            return 0.80
        elif price >= 5:
            return 0.65
        else:
            return 0.50
    
    # Default: assume moderate confidence
    return 0.50

def main():
    print("[START] Generating signals from database...")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    
    conn = sqlite3.connect('polymarket_data.db')
    cursor = conn.cursor()
    
    signals = []
    
    for strategy_name, params in STRATEGIES.items():
        category = params['category']
        
        print(f"\n[STRATEGY] {strategy_name}")
        print(f"  Category: {category}")
        print(f"  Win rate: {params['win_rate']*100:.1f}%")
        
        # Get markets in this category
        cursor.execute("""
            SELECT market_id, question, volume
            FROM markets
            WHERE category = ? AND active = 1
            ORDER BY volume DESC
        """, (category,))
        
        markets = cursor.fetchall()
        print(f"  Markets found: {len(markets)}")
        
        if not markets:
            continue
        
        # Check each market against strategy conditions
        matches = 0
        for market_id, question, volume in markets:
            # Estimate initial price
            price_proxy = extract_initial_price_proxy(question)
            
            # Check condition
            if params['condition'] == 'initial_price > 0.70':
                if price_proxy > 0.70:
                    signals.append({
                        'market_id': market_id,
                        'question': question,
                        'volume': volume,
                        'strategy': strategy_name,
                        'direction': params['direction'],
                        'win_rate': params['win_rate'],
                        'edge': params['edge'],
                        'price_estimate': price_proxy
                    })
                    matches += 1
        
        print(f"  Signals generated: {matches}")
    
    conn.close()
    
    # Display signals
    print(f"\n{'='*80}")
    print(f"[SIGNALS] Total: {len(signals)}")
    print('='*80)
    
    if not signals:
        print("  No signals found (no markets meet strategy conditions)")
        print("\n[NOTE] This is expected - most markets don't trigger strategies")
        print("       We need live price data to find real entry points")
    else:
        # Sort by win rate (highest first)
        signals.sort(key=lambda s: s['win_rate'], reverse=True)
        
        for i, sig in enumerate(signals, 1):
            print(f"\n[SIGNAL {i}]")
            print(f"  Market: {sig['question'][:70]}")
            print(f"  Volume: ${sig['volume']/1000:.0f}K")
            print(f"  Strategy: {sig['strategy']}")
            print(f"  Direction: {sig['direction']}")
            print(f"  Win rate: {sig['win_rate']*100:.1f}%")
            print(f"  Expected edge: {sig['edge']*100:.1f}%")
            print(f"  Price estimate: {sig['price_estimate']:.2f}")
    
    print(f"\n[DONE] Time: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
