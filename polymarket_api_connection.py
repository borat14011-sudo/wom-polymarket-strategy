"""
Polymarket API Connection Module
Uses credentials from saved API keys
"""
import requests
import json
from datetime import datetime

# API Credentials from PolyMarket_API.png
API_KEY = "019c3ee6-4d56-73fc-a7a2-e5db22b94340"
API_SECRET = "IZe8jb-on6PKYZY1G74Al-sTYeuEVPbFqH78e0f0xso="
API_PASSPHRASE = "b4736af6a2ef790b2034e258da2e296de866c60b4afe9ab707d3697b5c28b51f"

# Polymarket API Endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

def get_markets(limit=100, active=True):
    """Get list of markets from Gamma API"""
    url = f"{GAMMA_API}/markets"
    params = {
        "limit": limit,
        "active": active,
        "closed": False
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return None

def get_market_by_id(market_id):
    """Get specific market details"""
    url = f"{GAMMA_API}/markets/{market_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching market {market_id}: {e}")
        return None

def get_order_book(token_id):
    """Get order book for a specific token from CLOB API"""
    url = f"{CLOB_API}/book"
    params = {"token_id": token_id}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching order book: {e}")
        return None

def test_connection():
    """Test API connection by fetching markets"""
    print("Testing Polymarket API connection...")
    
    markets = get_markets(limit=5)
    
    if markets:
        print(f"Connection successful!")
        print(f"Found {len(markets)} markets")
        
        # Show first market as example
        if markets:
            market = markets[0]
            print(f"\nSample Market:")
            print(f"   Question: {market.get('question', 'N/A')}")
            print(f"   Status: {market.get('active', 'N/A')}")
            volume = market.get('volume', 0)
            try:
                volume_float = float(volume)
                print(f"   Volume: ${volume_float:,.2f}")
            except:
                print(f"   Volume: {volume}")
            
        return True
    else:
        print("Connection failed")
        return False

def get_live_prices(market_ids=None):
    """Get live prices for specified markets or top liquid markets"""
    markets = get_markets(limit=50)
    
    if not markets:
        return []
    
    prices = []
    for market in markets[:10]:  # Top 10 for now
        token_id = market.get('tokens', [{}])[0].get('token_id')
        
        if token_id:
            order_book = get_order_book(token_id)
            
            if order_book:
                # Calculate mid price from best bid/ask
                bids = order_book.get('bids', [])
                asks = order_book.get('asks', [])
                
                best_bid = float(bids[0]['price']) if bids else 0
                best_ask = float(asks[0]['price']) if asks else 0
                
                mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else best_bid or best_ask
                
                prices.append({
                    'question': market.get('question', 'N/A'),
                    'market_id': market.get('id'),
                    'token_id': token_id,
                    'best_bid': best_bid,
                    'best_ask': best_ask,
                    'mid_price': mid_price,
                    'spread': best_ask - best_bid if best_bid and best_ask else 0,
                    'volume': market.get('volume', 0)
                })
    
    return prices

if __name__ == "__main__":
    # Test connection
    test_connection()
    
    print("\n" + "="*50)
    print("Fetching live prices...")
    print("="*50)
    
    prices = get_live_prices()
    
    for p in prices[:5]:
        print(f"\n{p['question'][:60]}...")
        print(f"   Mid Price: {p['mid_price']:.4f} | Spread: {p['spread']:.4f}")
        print(f"   Bid: {p['best_bid']:.4f} | Ask: {p['best_ask']:.4f}")
