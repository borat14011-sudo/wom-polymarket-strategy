#!/usr/bin/env python3
"""
Execute first real trade with $10.41 wallet
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
print("EXECUTE FIRST REAL TRADE")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")
print(f"Balance: $10.41")

# Step 1: Get market data
print(f"\nStep 1: Getting market data...")
gamma_url = "https://gamma-api.polymarket.com/markets/517310"  # Trump deportation market
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    market = response.json()
    question = market.get('question', 'Unknown')
    condition_id = market.get('conditionId')
    outcomes = market.get('outcomes', [])
    
    print(f"Market: {question[:60]}...")
    print(f"Condition ID: {condition_id}")
    print(f"Outcomes: {outcomes}")
    
    # Get token_id for "Yes" outcome
    if "Yes" in outcomes:
        yes_index = outcomes.index("Yes") + 1
        token_id = condition_id + str(yes_index).zfill(2)
        print(f"Token ID for 'Yes': {token_id}")
        
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
            
            # Step 3: Create small test order
            print(f"\nStep 3: Creating test order...")
            
            # Get current price from order book
            orderbook_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
            ob_response = requests.get(orderbook_url, timeout=10)
            
            if ob_response.status_code == 200:
                orderbook = ob_response.json()
                asks = orderbook.get('asks', [])
                
                if asks:
                    best_ask = asks[0].get('price')
                    print(f"Best ask price: {best_ask}")
                    
                    # Create order at best ask price
                    order_args = OrderArgs(
                        token_id=token_id,
                        price=str(float(best_ask) + 0.01),  # Slightly above best ask
                        size="0.01",  # $0.01 test
                        side=BUY
                    )
                    
                    print(f"Order details:")
                    print(f"  Token: {token_id[:20]}...")
                    print(f"  Price: {order_args.price}")
                    print(f"  Size: {order_args.size}")
                    print(f"  Side: BUY")
                    
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
                        "market_id": "517310",
                        "question": question,
                        "token_id": token_id,
                        "price": order_args.price,
                        "size": order_args.size,
                        "side": "BUY",
                        "response": str(response)
                    }
                    
                    with open('first_trade.json', 'w') as f:
                        json.dump(trade_record, f, indent=2)
                    
                    print(f"\n" + "="*60)
                    print("SUCCESS! FIRST TRADE EXECUTED!")
                    print("="*60)
                    print(f"Traded: $0.01 on '{question[:40]}...'")
                    print(f"Price: {order_args.price}")
                    print(f"Wallet: {WALLET_ADDRESS}")
                    print(f"Record saved to: first_trade.json")
                    
                else:
                    print(f"No asks in order book")
            else:
                print(f"Orderbook error: {ob_response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
            print(f"\nTrying alternative approach...")
            
            # Try with different signature type
            try:
                client = ClobClient(
                    host="https://clob.polymarket.com",
                    chain_id=POLYGON,
                    key=PRIVATE_KEY,
                    signature_type=0,  # EIP-712
                    funder=WALLET_ADDRESS
                )
                
                print(f"Connected with signature_type=0")
                
                # Try simple API call
                balances = client.get_balances()
                print(f"Balances: {balances}")
                
            except Exception as e2:
                print(f"Alternative also failed: {e2}")
                
    else:
        print(f"'Yes' not in outcomes")
else:
    print(f"Market API error: {response.status_code}")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("1. Check Polymarket website for $0.01 trade")
print("2. If successful, scale up to $0.20 trades")
print("3. Enable full agent automation")
print("="*60)