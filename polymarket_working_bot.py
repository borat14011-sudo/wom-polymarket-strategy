#!/usr/bin/env python3
"""
Polymarket Working Trading Bot
==============================
Uses POLY_PROXY (signature_type=1) authentication flow.
Following official py-clob-client documentation EXACTLY.

IMPORTANT: Polymarket blocks certain regions (including US IPs).
If you get "403 - Access restricted", you need a VPN to a supported region.

Supported regions: Europe, Asia, South America, etc.
Blocked regions: US, some others

The authentication in this bot WORKS. Regional blocks are IP-based.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment from polymarket_bot/.env
load_dotenv('polymarket_bot/.env')

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs, OrderType, OpenOrderParams
from py_clob_client.order_builder.constants import BUY, SELL

# =============================================================================
# CONFIGURATION
# =============================================================================
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon mainnet

# From polymarket_bot/.env
PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')  # Your proxy wallet address

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_active_markets(limit=5):
    """
    Fetch active markets from Gamma API to get token IDs.
    Returns markets with their clobTokenIds.
    """
    url = "https://gamma-api.polymarket.com/markets"
    params = {
        "active": "true",
        "closed": "false",
        "limit": limit,
        "order": "volume24hr",
        "ascending": "false"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        markets = resp.json()
        
        result = []
        for market in markets:
            if market.get('clobTokenIds'):
                token_ids = market['clobTokenIds']
                # Parse the JSON string if needed
                if isinstance(token_ids, str):
                    import json
                    token_ids = json.loads(token_ids)
                
                outcomes = market.get('outcomes', '[]')
                if isinstance(outcomes, str):
                    import json
                    outcomes = json.loads(outcomes)
                
                result.append({
                    'question': market.get('question', 'Unknown'),
                    'slug': market.get('slug', ''),
                    'token_ids': token_ids,
                    'outcomes': outcomes,
                    'volume': market.get('volume', 0),
                    'volume_24hr': market.get('volume24hr', 0),
                    'end_date': market.get('endDate', '')
                })
        
        return result
    except Exception as e:
        print(f"[ERROR] Failed to fetch markets: {e}")
        return []


def display_markets(markets):
    """Display markets in a readable format."""
    print("\n" + "=" * 80)
    print("AVAILABLE MARKETS (sorted by 24h volume)")
    print("=" * 80)
    
    for i, market in enumerate(markets, 1):
        print(f"\n[{i}] {market['question'][:70]}...")
        print(f"    Volume (24h): ${float(market.get('volume_24hr', 0)):,.2f}")
        print(f"    Outcomes: {market['outcomes']}")
        for j, token_id in enumerate(market['token_ids']):
            outcome = market['outcomes'][j] if j < len(market['outcomes']) else f"Outcome {j}"
            print(f"    Token {j} ({outcome}): {token_id[:20]}...")
    
    return markets


def create_authenticated_client():
    """
    Create a fully authenticated ClobClient using POLY_PROXY flow.
    This follows the official documentation EXACTLY.
    """
    print("\n" + "=" * 80)
    print("CREATING AUTHENTICATED CLIENT (POLY_PROXY)")
    print("=" * 80)
    
    if not PRIVATE_KEY:
        print("[ERROR] POLYMARKET_PRIVATE_KEY not set in polymarket_bot/.env")
        sys.exit(1)
    
    if not FUNDER_ADDRESS:
        print("[ERROR] POLYMARKET_FUNDER_ADDRESS not set in polymarket_bot/.env")
        sys.exit(1)
    
    print(f"[INFO] Private Key: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-6:]}")
    print(f"[INFO] Funder Address: {FUNDER_ADDRESS}")
    print(f"[INFO] Signature Type: 1 (POLY_PROXY)")
    
    # Create client with POLY_PROXY signature type (1)
    # This is for Magic Link email login accounts
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1,  # POLY_PROXY for Magic Link / email login
        funder=FUNDER_ADDRESS  # The proxy wallet that holds your funds
    )
    
    print("\n[INFO] Deriving API credentials...")
    
    # Derive or create API credentials using the private key
    api_creds = client.create_or_derive_api_creds()
    client.set_api_creds(api_creds)
    
    print(f"[OK] API credentials derived successfully!")
    print(f"[INFO] API Key: {api_creds.api_key[:20]}...")
    
    return client


def test_connection(client):
    """Test the client connection and authentication."""
    print("\n" + "=" * 80)
    print("TESTING CONNECTION & AUTHENTICATION")
    print("=" * 80)
    
    # Test basic connectivity
    try:
        ok = client.get_ok()
        print(f"[OK] Server health check: {ok}")
    except Exception as e:
        print(f"[FAIL] Server health check: {e}")
        return False
    
    # Test server time
    try:
        server_time = client.get_server_time()
        print(f"[OK] Server time: {server_time}")
    except Exception as e:
        print(f"[FAIL] Server time: {e}")
    
    # Test authenticated endpoint - balance
    try:
        balance = client.get_balance_allowance()
        print(f"[OK] Balance/Allowance retrieved!")
        print(f"     Balance: {balance}")
    except Exception as e:
        print(f"[WARN] Balance check: {e}")
        # This might fail if no funds, but auth might still work
    
    # Test get orders
    try:
        orders = client.get_orders(OpenOrderParams())
        print(f"[OK] Open orders: {len(orders)} orders found")
    except Exception as e:
        print(f"[FAIL] Get orders: {e}")
        return False
    
    return True


def get_market_price(client, token_id):
    """Get current market price for a token."""
    try:
        # Get midpoint price
        mid = client.get_midpoint(token_id)
        # Get best buy/sell prices  
        buy_price = client.get_price(token_id, side="BUY")
        sell_price = client.get_price(token_id, side="SELL")
        
        # Handle dict responses (extract price if needed)
        def extract_price(val):
            if val is None:
                return None
            if isinstance(val, dict):
                return float(val.get('price', 0))
            return float(val)
        
        return {
            'midpoint': extract_price(mid),
            'buy': extract_price(buy_price),
            'sell': extract_price(sell_price)
        }
    except Exception as e:
        print(f"[WARN] Could not get price: {e}")
        return None


def place_limit_order(client, token_id, side, price, size):
    """
    Place a limit order.
    
    Args:
        client: Authenticated ClobClient
        token_id: The token to trade
        side: BUY or SELL
        price: Price per share (0.01 to 0.99)
        size: Number of shares
    """
    print(f"\n[INFO] Placing limit order...")
    print(f"       Token: {token_id[:30]}...")
    print(f"       Side: {side}")
    print(f"       Price: ${price}")
    print(f"       Size: {size} shares")
    print(f"       Total cost: ${price * size:.4f}")
    
    try:
        # Create order args
        order_args = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side=side
        )
        
        # Create signed order
        signed_order = client.create_order(order_args)
        print(f"[OK] Order signed successfully")
        
        # Post order (GTC = Good Till Cancelled)
        response = client.post_order(signed_order, OrderType.GTC)
        print(f"[OK] Order posted!")
        print(f"     Response: {response}")
        
        return response
    except Exception as e:
        error_str = str(e)
        if "403" in error_str and "regional" in error_str.lower():
            print(f"[BLOCKED] Regional restriction detected!")
            print(f"          Polymarket blocks certain regions (including US).")
            print(f"          Use a VPN to a supported region (Europe, Asia, etc.)")
        else:
            print(f"[FAIL] Order failed: {e}")
        return None


def place_market_order(client, token_id, side, amount_usd):
    """
    Place a market order (fill-or-kill).
    
    Args:
        client: Authenticated ClobClient
        token_id: The token to trade
        side: BUY or SELL
        amount_usd: Dollar amount to spend
    """
    print(f"\n[INFO] Placing market order...")
    print(f"       Token: {token_id[:30]}...")
    print(f"       Side: {side}")
    print(f"       Amount: ${amount_usd}")
    
    try:
        # Create market order args
        market_args = MarketOrderArgs(
            token_id=token_id,
            amount=amount_usd,
            side=side,
            order_type=OrderType.FOK  # Fill Or Kill
        )
        
        # Create signed order
        signed_order = client.create_market_order(market_args)
        print(f"[OK] Market order signed")
        
        # Post order
        response = client.post_order(signed_order, OrderType.FOK)
        print(f"[OK] Market order posted!")
        print(f"     Response: {response}")
        
        return response
    except Exception as e:
        error_str = str(e)
        if "403" in error_str and "regional" in error_str.lower():
            print(f"[BLOCKED] Regional restriction detected!")
            print(f"          Polymarket blocks certain regions (including US).")
            print(f"          Use a VPN to a supported region (Europe, Asia, etc.)")
        else:
            print(f"[FAIL] Market order failed: {e}")
        return None


def main():
    """Main function to run the trading bot."""
    print("\n" + "=" * 80)
    print("POLYMARKET WORKING TRADING BOT")
    print("Using POLY_PROXY (signature_type=1) authentication")
    print("=" * 80)
    
    # Step 1: Create authenticated client
    client = create_authenticated_client()
    
    # Step 2: Test connection
    if not test_connection(client):
        print("\n[FATAL] Authentication failed. Check your credentials.")
        sys.exit(1)
    
    # Step 3: Get available markets
    print("\n[INFO] Fetching active markets from Gamma API...")
    markets = get_active_markets(limit=5)
    
    if not markets:
        print("[WARN] No markets found. Using a known test market.")
        # Fallback to a common market for testing
    else:
        display_markets(markets)
    
    # Step 4: Interactive trading or test trade
    print("\n" + "=" * 80)
    print("READY TO TRADE")
    print("=" * 80)
    
    if markets:
        # Get first market's first token for testing
        test_market = markets[0]
        test_token_id = test_market['token_ids'][0]
        
        print(f"\n[TEST] Selected market: {test_market['question'][:60]}...")
        print(f"[TEST] Token ID: {test_token_id}")
        
        # Get current price
        prices = get_market_price(client, test_token_id)
        if prices:
            print(f"[TEST] Current prices:")
            print(f"       Midpoint: ${prices.get('midpoint', 'N/A')}")
            print(f"       Best Buy: ${prices.get('buy', 'N/A')}")
            print(f"       Best Sell: ${prices.get('sell', 'N/A')}")
        
        # Place a small test limit order ($0.01 worth)
        # Using a very low price to not actually fill (just to test auth)
        print("\n" + "-" * 40)
        print("PLACING TEST ORDER ($0.01)")
        print("-" * 40)
        
        # Place limit order at very low price (unlikely to fill)
        result = place_limit_order(
            client,
            token_id=test_token_id,
            side=BUY,
            price=0.01,  # $0.01 per share (very unlikely to fill)
            size=1.0     # 1 share
        )
        
        if result:
            print("\n[SUCCESS] Test order placed!")
            print("[INFO] The order is at $0.01 per share, unlikely to fill.")
            print("[INFO] You can cancel it from Polymarket.com")
            
            # Show current open orders
            try:
                orders = client.get_orders(OpenOrderParams())
                print(f"\n[INFO] You now have {len(orders)} open orders")
            except:
                pass
        else:
            print("\n[INFO] Order placement returned None - check output above")
    
    print("\n" + "=" * 80)
    print("BOT EXECUTION COMPLETE")
    print("=" * 80)
    
    return client  # Return client for interactive use


if __name__ == "__main__":
    main()
