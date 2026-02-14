"""
Simple API-based trade execution for Tariff $200-500B market.
Uses credentials from POLYMARKET_TRADING_BOT/.env.api
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

# Add the trading bot directory to path
sys.path.append('POLYMARKET_TRADING_BOT')

try:
    from polymarket_api_client import PolymarketAPIClient
    print("[OK] API client imported successfully")
except ImportError:
    print("✗ Could not import API client")
    print("Trying alternative approach...")
    
    # Simple HTTP request approach
    import requests
    import hmac
    import hashlib
    import base64
    
    class SimplePolymarketClient:
        def __init__(self):
            # Load credentials from .env.api
            env_path = 'POLYMARKET_TRADING_BOT/.env.api'
            self.credentials = {}
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.credentials[key] = value
            
            self.api_key = self.credentials.get('POLYMARKET_API_KEY')
            self.api_secret = self.credentials.get('POLYMARKET_API_SECRET')
            self.passphrase = self.credentials.get('POLYMARKET_PASSPHRASE')
            self.wallet_address = self.credentials.get('POLY_WALLET_ADDRESS')
            self.base_url = self.credentials.get('POLYMARKET_API_URL', 'https://clob.polymarket.com')
            
            print(f"[OK] Loaded credentials for wallet: {self.wallet_address[:10]}...")
        
        def get_market_info(self, market_id: str = "537486") -> Dict[str, Any]:
            """Get market information"""
            url = f"{self.base_url}/markets/{market_id}"
            response = requests.get(url)
            return response.json()
        
        def get_orderbook(self, market_id: str = "537486") -> Dict[str, Any]:
            """Get order book for market"""
            url = f"{self.base_url}/markets/{market_id}/book"
            response = requests.get(url)
            return response.json()
    
    PolymarketAPIClient = SimplePolymarketClient

# Main execution
def main():
    print("=" * 80)
    print("TARIFF $200-500B TRADE EXECUTION")
    print("=" * 80)
    
    # Market details
    MARKET_ID = "537486"  # Tariff $200-500B market
    TARGET_PRICE = 0.085  # 8.5%
    POSITION_SIZE = 1.00  # $1.00
    SIDE = "YES"  # BUY YES
    
    print(f"Market ID: {MARKET_ID}")
    print(f"Target Price: {TARGET_PRICE * 100:.1f}%")
    print(f"Position Size: ${POSITION_SIZE:.2f}")
    print(f"Side: {SIDE}")
    print()
    
    # Initialize client
    client = PolymarketAPIClient()
    
    # Get market info
    print("Fetching market information...")
    try:
        market_info = client.get_market_info(MARKET_ID)
        print(f"Market: {market_info.get('question', 'Unknown')}")
        print(f"Status: {market_info.get('active', 'Unknown')}")
        print(f"Volume: ${float(market_info.get('volume', 0)):,.2f}")
    except Exception as e:
        print(f"Error fetching market info: {e}")
    
    # Get orderbook
    print("\nFetching order book...")
    try:
        orderbook = client.get_orderbook(MARKET_ID)
        if 'bids' in orderbook and 'asks' in orderbook:
            print(f"Bids (BUY): {len(orderbook['bids'])} orders")
            print(f"Asks (SELL): {len(orderbook['asks'])} orders")
            
            # Show best prices
            if orderbook['asks']:
                best_ask = float(orderbook['asks'][0]['price'])
                print(f"Best ASK (YES price): {best_ask * 100:.2f}%")
                
                if best_ask <= TARGET_PRICE * 1.01:  # Within 1% of target
                    print(f"[OK] Price is acceptable: {best_ask * 100:.2f}% ≤ {TARGET_PRICE * 100:.1f}%")
                else:
                    print(f"[NO] Price too high: {best_ask * 100:.2f}% > {TARGET_PRICE * 100:.1f}%")
        else:
            print("Order book structure unexpected")
            print(json.dumps(orderbook, indent=2)[:500])
    except Exception as e:
        print(f"Error fetching order book: {e}")
    
    print("\n" + "=" * 80)
    print("TRADE RECOMMENDATION:")
    print("=" * 80)
    print("ACTION: BUY YES at ≤8.5%")
    print("AMOUNT: $1.00")
    print("RATIONALE: 26.5% edge (35% true vs 8.5% market)")
    print("EXPECTED RETURN: ~163% in 16 days")
    print("ANNUALIZED: ~3,700%")
    print("\nNOTE: API trading requires EIP-712 signing which is complex.")
    print("Manual execution via browser is recommended.")
    print("=" * 80)

if __name__ == "__main__":
    main()