#!/usr/bin/env python3
"""
Check all markets for order book status
"""

import requests
import json

print("="*60)
print("CHECKING ALL MARKETS FOR ORDER BOOK")
print("="*60)

# Get all active markets
gamma_url = "https://gamma-api.polymarket.com/markets?limit=50&closed=false"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    print(f"Found {len(markets)} active markets")
    
    markets_with_clob = []
    
    for market in markets:
        market_id = market.get('id')
        question = market.get('question', '')[:50]
        enable_order_book = market.get('enableOrderBook', False)
        clob_token_ids = market.get('clobTokenIds', [])
        
        if enable_order_book and clob_token_ids:
            markets_with_clob.append({
                'id': market_id,
                'question': question,
                'enableOrderBook': enable_order_book,
                'clobTokenIds': clob_token_ids,
                'volume24h': market.get('volume24h', 0)
            })
    
    print(f"\nMarkets with CLOB enabled: {len(markets_with_clob)}")
    
    # Show all markets with CLOB
    for i, market in enumerate(markets_with_clob):
        print(f"\n{i+1}. {market['question']}...")
        print(f"   ID: {market['id']}")
        print(f"   Volume 24h: ${market['volume24h']:,.0f}")
        print(f"   CLOB Token IDs: {len(market['clobTokenIds'])}")
        
        # Test first token ID
        token_id = market['clobTokenIds'][0]
        print(f"   Token ID: {token_id[:30]}...")
        
        # Test order book
        clob_base = "https://clob.polymarket.com"
        orderbook_url = f"{clob_base}/orderbook?token_id={token_id}"
        
        try:
            ob_response = requests.get(orderbook_url, timeout=5)
            if ob_response.status_code == 200:
                orderbook = ob_response.json()
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                print(f"   ✅ ORDER BOOK! Bids: {len(bids)}, Asks: {len(asks)}")
                
                # Save this market
                market_info = {
                    'market_id': market['id'],
                    'question': market['question'],
                    'token_id': token_id,
                    'has_order_book': True,
                    'bids_count': len(bids),
                    'asks_count': len(asks)
                }
                
                with open('working_market.json', 'w') as f:
                    json.dump(market_info, f, indent=2)
                print(f"   Saved to: working_market.json")
                
                break  # Found working market
            else:
                print(f"   ❌ Order book: {ob_response.status_code}")
        except Exception as e:
            print(f"   Error: {e}")
    
    if not markets_with_clob:
        print(f"\nNO MARKETS HAVE CLOB ENABLED!")
        print(f"This might mean:")
        print(f"1. All markets use AMM (Automated Market Maker) not CLOB")
        print(f"2. CLOB is disabled for these markets")
        print(f"3. We need to use AMM trading instead")
        
        # Check if markets use AMM
        print(f"\nChecking AMM prices...")
        for market in markets[:5]:
            market_id = market.get('id')
            question = market.get('question', '')[:40]
            outcome_prices = market.get('outcomePrices', [])
            
            print(f"\n{market_id}. {question}...")
            print(f"   Outcome prices: {outcome_prices}")
            print(f"   enableOrderBook: {market.get('enableOrderBook')}")
            
else:
    print(f"API error: {response.status_code}")

print("\n" + "="*60)
print("KEY INSIGHT")
print("="*60)
print("Polymarket might use AMM (Automated Market Maker) for most markets")
print("CLOB might only be for high-volume markets")
print("We might need to trade via AMM, not CLOB")
print("="*60)