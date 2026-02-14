import json

print("Loading raw_kalshi_response.json...")
with open('raw_kalshi_response.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Number of events: {len(data['events'])}")

# Load our top 10 bets
with open('top_10_kalshi_bets.json', 'r', encoding='utf-8') as f:
    top_bets = json.load(f)

print(f"\nSearching for partial matches...")

# Get all tickers from raw data
raw_tickers = [event.get('ticker', '') for event in data['events']]
print(f"Sample raw tickers: {raw_tickers[:10]}")

# Search for similar patterns
for bet in top_bets:
    ticker = bet['ticker']
    print(f"\nSearching for patterns similar to: {ticker}")
    
    # Try different search patterns
    search_terms = []
    
    # Remove the last part (e.g., -TOM)
    if '-' in ticker:
        base = ticker.rsplit('-', 1)[0]
        search_terms.append(base)
    
    # Try to find by market title keywords
    market_title = bet['market']
    keywords = market_title.lower().split()
    important_keywords = [kw for kw in keywords if len(kw) > 3 and kw not in ['will', 'be', 'the', 'next', 'in', 'of', 'before', 'jan', '1', '2045']]
    
    if important_keywords:
        print(f"  Keywords: {important_keywords[:3]}")
        
        # Search in raw data
        matches = []
        for event in data['events']:
            title = event.get('title', '').lower()
            if any(keyword in title for keyword in important_keywords[:3]):
                matches.append({
                    'ticker': event.get('ticker'),
                    'title': event.get('title'),
                    'status': event.get('status', 'N/A')
                })
        
        if matches:
            print(f"  Found {len(matches)} potential matches:")
            for match in matches[:3]:  # Show first 3
                print(f"    - {match['ticker']}: {match['title']} (Status: {match['status']})")
        else:
            print("  No matches found by keywords")