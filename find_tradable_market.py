#!/usr/bin/env python3
"""
Find a market that's actually tradable
"""

import requests
import json

print("="*60)
print("FINDING TRADABLE MARKET")
print("="*60)

# Get markets sorted by volume
markets_url = "https://gamma-api.polymarket.com/markets?limit=20&closed=false&sort=volume24h&order=desc"
response = requests.get(markets_url, timeout=10)

if response.status_code == 200:
    markets = response.json()
    print(f"Found {len(markets)} markets")
    
    tradable_markets = []
    
    for market in markets:
        market_id = market.get('id')
        question = market.get('question', '')[:50]
        volume24h = float(market.get('volume24h', 0))
        enable_order_book = market.get('enableOrderBook', False)
        clob_token_ids = market.get('clobTokenIds', [])
        
        # Only consider markets with volume > $1000
        if volume24h > 1000 and enable_order_book and clob_token_ids:
            # Get detailed market info
            market_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
            market_response = requests.get(market_url, timeout=5)
            
            if market_response.status_code == 200:
                market_details = market_response.json()
                
                # Check if it has bids/asks
                best_bid = market_details.get('bestBid')
                best_ask = market_details.get('bestAsk')
                
                if best_bid and best_ask:
                    tradable_markets.append({
                        'id': market_id,
                        'question': question,
                        'volume24h': volume24h,
                        'best_bid': best_bid,
                        'best_ask': best_ask,
                        'clob_token_ids': clob_token_ids
                    })
    
    print(f"\nFound {len(tradable_markets)} tradable markets")
    
    if tradable_markets:
        # Sort by volume
        tradable_markets.sort(key=lambda x: x['volume24h'], reverse=True)
        
        # Show top 3
        for i, market in enumerate(tradable_markets[:3]):
            print(f"\n{i+1}. {market['question']}...")
            print(f"   ID: {market['id']}")
            print(f"   24h Volume: ${market['volume24h']:,.0f}")
            print(f"   Best Bid: {market['best_bid']}")
            print(f"   Best Ask: {market['best_ask']}")
            print(f"   CLOB Token IDs: {len(market['clob_token_ids'])}")
            
            # Test order book with first token
            token_id = market['clob_token_ids'][0]
            print(f"   Token ID: {token_id[:30]}...")
            
            # Test CLOB orderbook
            orderbook_url = f"https://clob.polymarket.com/orderbook?token_id={token_id}"
            ob_response = requests.get(orderbook_url, timeout=5)
            
            if ob_response.status_code == 200:
                orderbook = ob_response.json()
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                print(f"   ✅ ORDER BOOK FOUND! Bids: {len(bids)}, Asks: {len(asks)}")
                
                # Save this market
                market_info = {
                    'market_id': market['id'],
                    'question': market['question'],
                    'token_id': token_id,
                    'best_bid': market['best_bid'],
                    'best_ask': market['best_ask'],
                    'has_order_book': True
                }
                
                with open('tradable_market.json', 'w') as f:
                    json.dump(market_info, f, indent=2)
                print(f"   Saved to: tradable_market.json")
                
                break  # Found working market
            else:
                print(f"   ❌ Order book: {ob_response.status_code}")
    else:
        print(f"\nNO TRADABLE MARKETS FOUND!")
        print(f"This suggests:")
        print(f"1. Markets might use AMM, not CLOB")
        print(f"2. CLOB might be disabled")
        print(f"3. Need to use website trading")
        
        # Show top markets anyway
        print(f"\nTop 3 markets by volume:")
        for i, market in enumerate(markets[:3]):
            market_id = market.get('id')
            question = market.get('question', '')[:50]
            volume24h = float(market.get('volume24h', 0))
            enable_order_book = market.get('enableOrderBook', False)
            
            print(f"\n{i+1}. {question}...")
            print(f"   ID: {market_id}")
            print(f"   24h Volume: ${volume24h:,.0f}")
            print(f"   Enable Order Book: {enable_order_book}")
            
else:
    print(f"API error: {response.status_code}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("If no tradable markets found, we need to:")
print("1. Use website trading (manual or automated)")
print("2. Find AMM trading endpoints")
print("3. Or wait for markets to get order books")
print("="*60)