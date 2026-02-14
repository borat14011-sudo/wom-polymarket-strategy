#!/usr/bin/env python3
"""
Find a market that definitely has an order book
"""

import requests
import json

print("="*60)
print("FINDING MARKET WITH ORDER BOOK")
print("="*60)

# Get markets with high volume (more likely to have order book)
gamma_url = "https://gamma-api.polymarket.com/events?closed=false&limit=20"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    events = response.json()
    
    markets_with_orderbook = []
    
    for event in events:
        for market in event.get('markets', []):
            market_id = market.get('id')
            question = market.get('question', '')[:60]
            volume24h = market.get('volume24h', 0)
            enable_order_book = market.get('enableOrderBook', False)
            
            # Check if market has order book enabled AND high volume
            if enable_order_book and volume24h > 1000:
                # Get market details to check clobTokenIds
                market_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
                market_response = requests.get(market_url, timeout=5)
                
                if market_response.status_code == 200:
                    market_details = market_response.json()
                    
                    # Check if it has clobTokenIds
                    clob_token_ids_str = market_details.get('clobTokenIds', '[]')
                    if clob_token_ids_str != '[]':
                        import ast
                        try:
                            clob_token_ids = ast.literal_eval(clob_token_ids_str)
                            if clob_token_ids:
                                markets_with_orderbook.append({
                                    'id': market_id,
                                    'question': question,
                                    'volume24h': volume24h,
                                    'clob_token_ids': clob_token_ids,
                                    'bestBid': market_details.get('bestBid'),
                                    'bestAsk': market_details.get('bestAsk')
                                })
                        except:
                            pass
    
    print(f"Found {len(markets_with_orderbook)} markets with order book enabled")
    
    # Sort by volume
    markets_with_orderbook.sort(key=lambda x: x['volume24h'], reverse=True)
    
    # Show top 5
    for i, market in enumerate(markets_with_orderbook[:5]):
        print(f"\n{i+1}. {market['question']}...")
        print(f"   ID: {market['id']}")
        print(f"   24h Volume: ${market['volume24h']:,.0f}")
        print(f"   Best Bid: {market.get('bestBid')}")
        print(f"   Best Ask: {market.get('bestAsk')}")
        print(f"   CLOB Token IDs: {len(market['clob_token_ids'])}")
        
        # Test first token ID
        if market['clob_token_ids']:
            token_id = market['clob_token_ids'][0]
            print(f"   First token ID: {token_id[:30]}...")
            
            # Test order book
            clob_base = "https://clob.polymarket.com"
            orderbook_url = f"{clob_base}/orderbook?token_id={token_id}"
            ob_response = requests.get(orderbook_url, timeout=5)
            
            if ob_response.status_code == 200:
                orderbook = ob_response.json()
                bids = orderbook.get('bids', [])
                asks = orderbook.get('asks', [])
                print(f"   ✅ ORDER BOOK FOUND! Bids: {len(bids)}, Asks: {len(asks)}")
                
                # Save this market for trading
                market_info = {
                    'market_id': market['id'],
                    'question': market['question'],
                    'token_id': token_id,
                    'best_bid': bids[0].get('price') if bids else None,
                    'best_ask': asks[0].get('price') if asks else None
                }
                
                with open('market_with_orderbook.json', 'w') as f:
                    json.dump(market_info, f, indent=2)
                print(f"   Saved to: market_with_orderbook.json")
                
                break  # Found working market
            else:
                print(f"   ❌ Order book error: {ob_response.status_code}")
    
    if not markets_with_orderbook:
        print(f"\nNo markets with order book found")
        
else:
    print(f"API error: {response.status_code}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("We need a market with:")
print("1. enableOrderBook: true")
print("2. clobTokenIds array not empty")
print("3. Actual order book on CLOB API")
print("="*60)