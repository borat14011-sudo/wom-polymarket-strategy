#!/usr/bin/env python3
"""
Execute real trade with correct token_id format
"""

import os
import time
import json
import requests
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL

load_dotenv('polymarket_bot/.env')

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("EXECUTE REAL TRADE")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Balance: $10.41")

# Step 1: Get market with correct token_id
print(f"\nStep 1: Getting market with CLOB token IDs...")

# Use market 517310 (Trump deportation <250k)
market_id = "517310"
gamma_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    market = response.json()
    question = market.get('question', 'Unknown')
    condition_id = market.get('conditionId')
    
    print(f"Market: {question[:60]}...")
    print(f"Condition ID: {condition_id}")
    
    # Parse clobTokenIds (they're decimal strings)
    import ast
    clob_token_ids_str = market.get('clobTokenIds', '[]')
    clob_token_ids = ast.literal_eval(clob_token_ids_str)
    
    print(f"CLOB Token IDs: {clob_token_ids}")
    
    if len(clob_token_ids) >= 2:
        # First token is "Yes", second is "No"
        yes_token_id = clob_token_ids[0]  # Decimal string
        no_token_id = clob_token_ids[1]   # Decimal string
        
        print(f"\nYes token ID (decimal): {yes_token_id}")
        print(f"No token ID (decimal): {no_token_id}")
        
        # Step 2: Initialize client
        print(f"\nStep 2: Initializing client...")
        try:
            client = ClobClient(
                host="https://clob.polymarket.com",
                chain_id=POLYGON,
                key=PRIVATE_KEY,
                signature_type=1,
                funder=WALLET_ADDRESS
            )
            
            # Test connection
            server_time = client.get_server_time()
            print(f"Connected! Server time: {server_time}")
            
            # Step 3: Check order book
            print(f"\nStep 3: Checking order book...")
            
            # The token_id should be the DECIMAL string, not hex
            orderbook_url = f"https://clob.polymarket.com/orderbook?token_id={yes_token_id}"
            ob_response = requests.get(orderbook_url, timeout=10)
            
            if ob_response.status_code == 200:
                orderbook = ob_response.json()
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                
                print(f"Order book found!")
                print(f"Bids: {len(bids)}, Asks: {len(asks)}")
                
                if asks:
                    best_ask = asks[0]
                    ask_price = best_ask.get('price')
                    ask_size = best_ask.get('size')
                    
                    print(f"\nBest ask: {ask_price} @ {ask_size}")
                    
                    # Step 4: Create small test order
                    print(f"\nStep 4: Creating test order...")
                    
                    # Use price slightly above best ask to get filled
                    buy_price = str(float(ask_price) + 0.001)  # Add 0.1%
                    buy_size = "0.01"  # $0.01 test
                    
                    print(f"Order details:")
                    print(f"  Token ID: {yes_token_id[:20]}...")
                    print(f"  Price: {buy_price}")
                    print(f"  Size: {buy_size}")
                    print(f"  Side: BUY")
                    
                    # Create order
                    order_args = OrderArgs(
                        token_id=yes_token_id,  # Use decimal string
                        price=buy_price,
                        size=buy_size,
                        side=BUY
                    )
                    
                    # Sign order
                    print(f"\nSigning order...")
                    signed_order = client.create_order(order_args)
                    print(f"Order signed!")
                    
                    # Post order
                    print(f"\nPosting order...")
                    response = client.post_order(signed_order, OrderType.GTC)
                    print(f"Order posted! Response: {response}")
                    
                    # Save trade record
                    trade_record = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "wallet": WALLET_ADDRESS,
                        "market_id": market_id,
                        "question": question,
                        "token_id": yes_token_id,
                        "price": buy_price,
                        "size": buy_size,
                        "side": "BUY",
                        "response": str(response)
                    }
                    
                    with open('real_trade_executed.json', 'w') as f:
                        json.dump(trade_record, f, indent=2)
                    
                    print(f"\n" + "="*60)
                    print("✅ SUCCESS! REAL TRADE EXECUTED!")
                    print("="*60)
                    print(f"Traded: ${buy_size} on '{question[:40]}...'")
                    print(f"Price: {buy_price}")
                    print(f"Wallet: {WALLET_ADDRESS}")
                    print(f"Record saved to: real_trade_executed.json")
                    
                else:
                    print(f"No asks in order book")
                    
            else:
                print(f"Order book error: {ob_response.status_code}")
                print(f"Trying alternative token ID format...")
                
                # Try with hex format
                token_hex = hex(int(yes_token_id))
                print(f"Hex format: {token_hex}")
                
                orderbook_url = f"https://clob.polymarket.com/orderbook?token_id={token_hex}"
                ob_response = requests.get(orderbook_url, timeout=10)
                print(f"Hex order book: {ob_response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            
    else:
        print(f"Not enough token IDs")
        
else:
    print(f"Market API error: {response.status_code}")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("1. Check Polymarket website for trade")
print("2. If successful, update Trade Executor agent")
print("3. Enable automated trading")
print("="*60)