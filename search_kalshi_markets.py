import json

# Load the top 10 bets
with open('top_10_kalshi_bets.json', 'r') as f:
    top_bets = json.load(f)

# Load the kalshi data
print("Loading kalshi data...")
with open('kalshi_latest.json', 'r') as f:
    kalshi_data = json.load(f)

print(f"Total events in kalshi data: {len(kalshi_data.get('events', []))}")

# Search for each market
for bet in top_bets:
    ticker = bet['ticker']
    print(f"\nSearching for: {ticker} - {bet['market']}")
    
    found = False
    for event in kalshi_data.get('events', []):
        if event.get('ticker') == ticker:
            print(f"  Found! Status: {event.get('status', 'unknown')}")
            print(f"  Title: {event.get('title', 'N/A')}")
            
            # Check markets within the event
            for market in event.get('markets', []):
                print(f"  Market ID: {market.get('id')}")
                print(f"  Market Status: {market.get('status')}")
                print(f"  Close Date: {market.get('close_date')}")
                print(f"  Expiration Date: {market.get('expiration_date')}")
            
            found = True
            break
    
    if not found:
        print(f"  NOT FOUND in kalshi data")
        
print("\nDone searching.")