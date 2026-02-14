#!/usr/bin/env python3
"""
Debug market fetching
"""

from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

private_key = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

try:
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=private_key)
    print("Client initialized")
    
    # Try different market methods
    print("\nTrying get_markets()...")
    try:
        markets = client.get_markets()
        print(f"get_markets returned: {type(markets)}")
        if isinstance(markets, list):
            print(f"Length: {len(markets)}")
            if markets:
                print(f"First market: {markets[0]}")
        else:
            print(f"Value: {markets}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nTrying get_simplified_markets()...")
    try:
        simple = client.get_simplified_markets()
        print(f"get_simplified_markets returned: {type(simple)}")
        if isinstance(simple, list):
            print(f"Length: {len(simple)}")
            if simple:
                print(f"First: {simple[0]}")
    except Exception as e:
        print(f"Error: {e}")
        
except Exception as e:
    print(f"Client error: {e}")