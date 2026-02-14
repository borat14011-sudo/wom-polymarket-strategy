#!/usr/bin/env python3
"""
Find ANY market with working order book
"""

import requests
import json

print("="*60)
print("FIND ANY WORKING MARKET")
print("="*60)

# Get ALL markets
markets_url = "https://gamma-api.polymarket.com/markets?limit=100&closed=false"
response = requests.get(markets_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    print(f"Found {len(markets)} markets")
    
    working_markets = []
    
    for market in markets:
        market_id = market.get('id')
        question = market.get('question', '')[:50]
        enable_order_book = market.get('enableOrderBook', False)
        clob_token_ids_str = market.get('clobTokenIds', '[]')
        
        if enable_order_book and clob_token_ids_str != '[]':
            try:
                clob_token_ids = json.loads(clob_token_ids_str)
                if clob_token_ids:
                    # Test first token
                    token_id = clob_token_ids[0]
                    
                    # Test order book
                    orderbook_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
                    ob_response = requests.get(orderbook_url, timeout=5)
                    
                    if ob_response.status_code == 200:
                        orderbook = ob_response.json()
                        bids = orderbook.get('bids', [])
                        asks = orderbook.get('asks', [])
                        
                        if bids or asks:
                            working_markets.append({
                                'id': market_id,
                                'question': question,
                                'token_id': token_id,
                                'bids': len(bids),
                                'asks': len(asks)
                            })
                            
                            # Stop after finding 1
                            break
            except:
                pass
    
    print(f"\nFound {len(working_markets)} markets with working order book")
    
    if working_markets:
        for market in working_markets:
            print(f"\n✅ WORKING MARKET FOUND!")
            print(f"ID: {market['id']}")
            print(f"Question: {market['question']}...")
            print(f"Token ID: {market['token_id'][:30]}...")
            print(f"Bids: {market['bids']}, Asks: {market['asks']}")
            
            # Save for trading
            market_info = {
                'market_id': market['id'],
                'question': market['question'],
                'token_id': market['token_id'],
                'has_order_book': True
            }
            
            with open('working_market_found.json', 'w') as f:
                json.dump(market_info, f, indent=2)
            print(f"Saved to: working_market_found.json")
            
            break  # Just need one
    else:
        print(f"\n❌ NO MARKETS WITH WORKING ORDER BOOK!")
        print(f"This confirms: CLOB trading might not be available")
        print(f"We need to use: Website trading or AMM")
        
        # Show what we have
        print(f"\nChecking first 5 markets:")
        for i, market in enumerate(markets[:5]):
            market_id = market.get('id')
            question = market.get('question', '')[:40]
            enable_order_book = market.get('enableOrderBook', False)
            volume24h = market.get('volume24h', 0)
            
            print(f"\n{i+1}. {question}...")
            print(f"   ID: {market_id}")
            print(f"   Order Book: {enable_order_book}")
            print(f"   24h Volume: {volume24h}")
            
else:
    print(f"API error: {response.status_code}")

print("\n" + "="*60)
print("FINAL CONCLUSION")
print("="*60)
print("If NO working order books found:")
print("1. CLOB API trading is NOT available")
print("2. Must use website trading (manual or automated)")
print("3. Or find AMM trading endpoints")
print("\nACTION: Try manual website trade NOW!")
print("="*60)