import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

def get_all_markets():
    """Get all active markets"""
    url = f"{GAMMA_API}/markets"
    params = {"limit": 500, "active": True, "closed": False}
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_order_book(token_id):
    """Get order book for token"""
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

def find_super_bowl_markets():
    """Find all Super Bowl related markets"""
    markets = get_all_markets()
    
    sb_keywords = ['super bowl', 'superbowl', 'sb lix', 'sb59', 'chiefs', 'eagles', 'mahomes', 'hurts']
    sb_markets = []
    
    for market in markets:
        question = market.get('question', '').lower()
        description = market.get('description', '').lower()
        
        if any(kw in question or kw in description for kw in sb_keywords):
            # Get price data
            tokens = market.get('tokens', [])
            if tokens:
                token = tokens[0]
                token_id = token.get('token_id')
                ob = get_order_book(token_id)
                
                if ob:
                    bids = ob.get('bids', [])
                    asks = ob.get('asks', [])
                    best_bid = float(bids[0]['price']) if bids else 0
                    best_ask = float(asks[0]['price']) if asks else 0
                    mid = (best_bid + best_ask) / 2 if best_bid and best_ask else best_bid or best_ask
                    
                    market['live_bid'] = best_bid
                    market['live_ask'] = best_ask
                    market['live_mid'] = mid
                    market['live_spread'] = best_ask - best_bid if best_bid and best_ask else 0
            
            sb_markets.append(market)
    
    return sb_markets

if __name__ == "__main__":
    print("=" * 60)
    print("SUPER BOWL LIX MARKETS - LIVE ODDS")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%I:%M %p PT')}")
    print("=" * 60)
    
    markets = find_super_bowl_markets()
    
    # Sort by volume
    markets.sort(key=lambda x: float(x.get('volume', 0) or 0), reverse=True)
    
    print(f"\nFound {len(markets)} Super Bowl markets:\n")
    
    for i, m in enumerate(markets[:20], 1):
        question = m.get('question', 'N/A')
        volume = m.get('volume', 0)
        try:
            vol_str = f"${float(volume):,.0f}"
        except:
            vol_str = f"${volume}"
        
        mid = m.get('live_mid', 0)
        spread = m.get('live_spread', 0)
        
        print(f"{i}. {question}")
        print(f"   Volume: {vol_str} | Price: {mid:.2%} | Spread: {spread:.1%}")
        print()
