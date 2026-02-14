#!/usr/bin/env python3
"""
Test using official py-clob-client example
"""

import os
from dotenv import load_dotenv

load_dotenv('polymarket_bot/.env')
PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("Testing official SDK example...")
print(f"Wallet: {WALLET_ADDRESS}")

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.constants import POLYGON
    from py_clob_client.clob_types import OrderArgs
    from py_clob_client.order_builder.constants import BUY, SELL
    
    # Initialize client
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=POLYGON,
        key=PRIVATE_KEY,
        signature_type=1,
        funder=WALLET_ADDRESS
    )
    
    print(f"Connected! Server time: {client.get_server_time()}")
    
    # Get markets to find token_id
    print("\nGetting markets...")
    markets = client.get_simplified_markets()
    
    if markets:
        print(f"Found {len(markets)} markets")
        
        # Look at first market
        first_market = markets[0]
        print(f"\nFirst market: {first_market}")
        
        # The market should have token_id or condition_id
        if isinstance(first_market, dict):
            market_id = first_market.get('id')
            condition_id = first_market.get('conditionId')
            print(f"Market ID: {market_id}")
            print(f"Condition ID: {condition_id}")
            
            # Try to get order book to see tokens
            print(f"\nGetting order book for market {market_id}...")
            try:
                order_book = client.get_order_book(market_id)
                print(f"Order book: {order_book}")
                
                # Look for tokens in order book
                if order_book and isinstance(order_book, dict):
                    tokens = order_book.get('tokens', [])
                    if tokens:
                        print(f"Tokens: {tokens}")
                        token_id = tokens[0]
                        print(f"\nUsing token_id: {token_id}")
                        
                        # Try to create order
                        print(f"\nCreating test order with token_id: {token_id}")
                        order_args = OrderArgs(
                            token_id=token_id,
                            price=0.50,
                            size=0.20,
                            side=BUY
                        )
                        
                        print(f"OrderArgs: {order_args}")
                        
                        # Try to create order
                        order = client.create_and_post_order(order_args)
                        print(f"Order response: {order}")
                        
                    else:
                        print("No tokens in order book")
                else:
                    print(f"Order book type: {type(order_book)}")
                    
            except Exception as e:
                print(f"Order book error: {e}")
                
        else:
            print(f"Market is not a dict: {type(first_market)}")
            
    else:
        print("No markets found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("ALTERNATIVE: Use existing test_trade_execution.py")
print("="*60)
print("We already have a working test_trade_execution.py")
print("Let me run that instead...")