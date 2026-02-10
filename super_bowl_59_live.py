import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

def get_all_markets():
    url = f"{GAMMA_API}/markets"
    params = {"limit": 1000, "active": True, "closed": False}
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_order_book(token_id):
    if not token_id:
        return None
    url = f"{CLOB_API}/book"
    params = {"token_id": token_id}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except:
        return None

def find_sb59_markets():
    """Find Super Bowl 59 / LIX markets for tonight's game"""
    markets = get_all_markets()
    
    # Keywords for tonight's game
    keywords = ['chiefs', 'eagles', 'mahomes', 'hurts', 'kelce', 'super bowl 59', 'sb59', 'sb 59']
    sb59_markets = []
    
    for market in markets:
        question = market.get('question', '').lower()
        description = market.get('description', '').lower()
        
        # Must contain SB59 keyword
        is_sb59 = any(kw in question for kw in keywords)
        
        # Filter out 2026 markets
        is_2026 = '2026' in question or 'lx' in question or '60' in question
        
        if is_sb59 and not is_2026:
            tokens = market.get('tokens', [])
            outcomes = []
            
            for token in tokens:
                token_id = token.get('token_id')
                outcome = token.get('outcome', 'Unknown')
                ob = get_order_book(token_id)
                
                if ob:
                    bids = ob.get('bids', [])
                    asks = ob.get('asks', [])
                    best_bid = float(bids[0]['price']) if bids else 0
                    best_ask = float(asks[0]['price']) if asks else 0
                    mid = (best_bid + best_ask) / 2 if best_bid and best_ask else best_bid or best_ask
                    
                    outcomes.append({
                        'outcome': outcome,
                        'mid': mid,
                        'bid': best_bid,
                        'ask': best_ask,
                        'spread': best_ask - best_bid if best_bid and best_ask else 0
                    })
            
            market['outcomes'] = outcomes
            market['num_outcomes'] = len(outcomes)
            sb59_markets.append(market)
    
    return sb59_markets

if __name__ == "__main__":
    print("=" * 70)
    print("SUPER BOWL LIX TONIGHT - CHIEFS vs EAGLES")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%I:%M %p PT')} | Game: 6:30 PM ET")
    print("=" * 70)
    
    markets = find_sb59_markets()
    
    # Sort by volume
    markets.sort(key=lambda x: float(x.get('volume', 0) or 0), reverse=True)
    
    print(f"\nFound {len(markets)} Super Bowl 59 markets for TONIGHT:\n")
    
    for i, m in enumerate(markets[:15], 1):
        question = m.get('question', 'N/A')
        volume = m.get('volume', 0)
        try:
            vol_str = f"${float(volume):,.0f}"
        except:
            vol_str = f"${volume}"
        
        print(f"\n{i}. {question}")
        print(f"   Volume: {vol_str}")
        
        for outcome in m.get('outcomes', []):
            name = outcome['outcome']
            mid = outcome['mid']
            spread = outcome['spread']
            print(f"   → {name}: {mid:.1%} (spread {spread:.1%})")
