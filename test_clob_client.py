"""Test py-clob-client for historical data access"""
import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from py_clob_client.client import ClobClient
import json
from datetime import datetime, timedelta

print("=== Testing py-clob-client ===\n")

# Initialize client (read-only mode, no authentication needed)
try:
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137  # Polygon mainnet
    )
    print("[OK] Client initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize client: {e}")
    sys.exit(1)

# Test getting markets
print("\n=== Testing market access ===")
try:
    # Get active markets
    markets = client.get_markets()
    print(f"[OK] Retrieved {len(markets)} markets")
    
    if markets:
        sample = markets[0]
        print(f"\nSample market structure:")
        print(f"  Question: {sample.get('question', 'N/A')[:60]}")
        print(f"  Keys: {list(sample.keys())[:15]}")
        
        # Check if condition_id exists
        condition_id = sample.get('condition_id')
        print(f"  Condition ID: {condition_id}")
        
except Exception as e:
    print(f"[ERROR] {e}")

# Test price history access
print("\n=== Testing price history ===")
try:
    # Try different methods to get price history
    
    # Method 1: Check if client has price history method
    if hasattr(client, 'get_price_history'):
        print("[FOUND] Client has get_price_history method")
    else:
        print("[INFO] No direct get_price_history method")
    
    # Method 2: Check all available methods
    methods = [m for m in dir(client) if not m.startswith('_')]
    print(f"\nAvailable client methods:")
    for method in methods[:20]:
        print(f"  - {method}")
    
    # Method 3: Try to get price data from a specific market
    if markets:
        market = markets[0]
        token_id = None
        
        # Try to find token IDs
        if 'tokens' in market:
            tokens = market['tokens']
            if tokens and len(tokens) > 0:
                token_id = tokens[0].get('token_id')
                print(f"\n  Testing with token ID: {token_id}")
        
        if token_id:
            # Try various client methods
            methods_to_try = [
                ('get_trades', {'market': token_id}),
                ('get_tick_size', {'token_id': token_id}),
            ]
            
            for method_name, params in methods_to_try:
                if hasattr(client, method_name):
                    try:
                        result = getattr(client, method_name)(**params)
                        print(f"  [OK] {method_name}: {str(result)[:100]}")
                    except Exception as e:
                        print(f"  [FAIL] {method_name}: {str(e)[:80]}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# Check documentation
print("\n=== Client Documentation ===")
if client.__doc__:
    print(client.__doc__[:500])
else:
    print("No documentation available")

print("\n=== Recommendation ===")
print("The py-clob-client is primarily for trading, not historical data.")
print("We should use direct Gamma API + custom price history scraping.")
