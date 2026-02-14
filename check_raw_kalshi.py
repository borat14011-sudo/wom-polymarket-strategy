import json

print("Loading raw_kalshi_response.json...")
with open('raw_kalshi_response.json', 'r') as f:
    data = json.load(f)

print(f"Data type: {type(data)}")

if isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    if 'events' in data:
        print(f"Number of events: {len(data['events'])}")
        
        # Load our top 10 bets
        with open('top_10_kalshi_bets.json', 'r') as f:
            top_bets = json.load(f)
        
        print(f"\nSearching for {len(top_bets)} tickers in raw data...")
        
        found_count = 0
        for bet in top_bets:
            ticker = bet['ticker']
            found = False
            
            for event in data['events']:
                if event.get('ticker') == ticker:
                    print(f"\n✓ FOUND: {ticker}")
                    print(f"  Title: {event.get('title', 'N/A')}")
                    print(f"  Status: {event.get('status', 'N/A')}")
                    
                    # Check market details
                    markets = event.get('markets', [])
                    if markets:
                        market = markets[0]
                        print(f"  Market Status: {market.get('status')}")
                        print(f"  Close Date: {market.get('close_date')}")
                    
                    found = True
                    found_count += 1
                    break
            
            if not found:
                print(f"\n✗ NOT FOUND: {ticker}")
        
        print(f"\nSummary: Found {found_count} out of {len(top_bets)} markets")
        
elif isinstance(data, list):
    print(f"List length: {len(data)}")
    # Check first few items
    for i, item in enumerate(data[:5]):
        print(f"\nItem {i}: Type: {type(item)}")
        if isinstance(item, dict):
            print(f"  Keys: {list(item.keys())}")
            if 'ticker' in item:
                print(f"  Ticker: {item['ticker']}")