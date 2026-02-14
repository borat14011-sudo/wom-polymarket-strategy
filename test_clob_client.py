#!/usr/bin/env python3
"""
Test py-clob-client to make a trade
"""

import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from web3 import Web3

load_dotenv('polymarket_bot/.env')

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("TEST CLOB CLIENT")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")

if not PRIVATE_KEY or not WALLET_ADDRESS:
    print("❌ Missing credentials in .env file")
    exit(1)

# Initialize client
try:
    host = "https://clob.polymarket.com"
    chain_id = 137  # Polygon
    
    client = ClobClient(host, chain_id=chain_id, signature_type=1)
    print(f"✅ Client initialized")
    
    # Get time
    time_response = client.get_time()
    print(f"Time: {time_response}")
    
    # Get markets to find a token_id that works
    # Let's try to get orderbook for a known token
    # First, get a market from Gamma API
    import requests
    markets_url = "https://gamma-api.polymarket.com/markets?limit=5&closed=false"
    response = requests.get(markets_url, timeout=10)
    
    if response.status_code == 200:
        markets = response.json()
        print(f"\nFound {len(markets)} markets")
        
        for market in markets:
            market_id = market.get('id')
            question = market.get('question', '')[:50]
            
            # Get market details
            market_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
            market_response = requests.get(market_url, timeout=5)
            
            if market_response.status_code == 200:
                market_details = market_response.json()
                clob_token_ids_str = market_details.get('clobTokenIds', '[]')
                
                import json
                try:
                    clob_token_ids = json.loads(clob_token_ids_str)
                    if clob_token_ids:
                        token_id = clob_token_ids[0]
                        
                        print(f"\nMarket: {question}...")
                        print(f"Token ID: {token_id}")
                        
                        # Try to get orderbook
                        try:
                            orderbook = client.get_orderbook(token_id)
                            print(f"✅ Orderbook found!")
                            print(f"   Bids: {len(orderbook.bids)}")
                            print(f"   Asks: {len(orderbook.asks)}")
                            
                            if orderbook.asks:
                                # Try to place a small buy order
                                print(f"\nTrying to place test order...")
                                
                                # Get best ask price
                                best_ask = orderbook.asks[0]
                                price = float(best_ask.price)
                                size = 0.01  # $0.01
                                
                                print(f"Best ask: {price}")
                                print(f"Size: {size}")
                                
                                # Create order
                                order_args = OrderArgs(
                                    price=price,
                                    size=size,
                                    side=BUY,
                                    token_id=token_id
                                )
                                
                                # Sign order
                                signed_order = client.create_order(order_args)
                                print(f"✅ Order created: {signed_order}")
                                
                                # Post order
                                order_response = client.post_order(signed_order, PRIVATE_KEY)
                                print(f"✅ Order posted: {order_response}")
                                
                                break  # Stop after first successful market
                                
                        except Exception as e:
                            print(f"❌ Orderbook error: {e}")
                            
                except Exception as e:
                    print(f"❌ Parse error: {e}")
                    
    else:
        print(f"❌ Gamma API error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Client error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("If this works, we have a working trading method!")
print("If not, we need to try something else.")
print("="*60)