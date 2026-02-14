import json
from datetime import datetime, timezone

# Load the data
with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    markets = json.load(f)

# Check for resolved/finalized markets
resolved_markets = []
active_markets = []

for market in markets:
    status = market.get('status', '')
    if status.lower() in ['finalized', 'settled', 'resolved']:
        resolved_markets.append(market)
    elif status.lower() == 'active':
        active_markets.append(market)

print(f"Total markets: {len(markets)}")
print(f"Active markets: {len(active_markets)}")
print(f"Resolved/finalized markets: {len(resolved_markets)}")

# Check if we have resolution data for any markets
if resolved_markets:
    print("\nSample of resolved markets:")
    for i, market in enumerate(resolved_markets[:5]):
        print(f"{i+1}. {market.get('ticker_name', 'N/A')}: {market.get('status', 'N/A')}")
        
    # Check if we have last_price data that might indicate resolution outcome
    print("\nChecking for resolution outcomes...")
    yes_resolved = 0
    no_resolved = 0
    unknown = 0
    
    for market in resolved_markets:
        last_price = market.get('last_price')
        if last_price is not None:
            if last_price == 100:
                yes_resolved += 1
            elif last_price == 0:
                no_resolved += 1
            else:
                unknown += 1
        else:
            unknown += 1
    
    print(f"Resolved YES (100¢): {yes_resolved}")
    print(f"Resolved NO (0¢): {no_resolved}")
    print(f"Unknown resolution: {unknown}")
    
    if yes_resolved + no_resolved > 0:
        win_rate = yes_resolved / (yes_resolved + no_resolved) * 100
        print(f"\nActual Kalshi win rate (from resolved markets): {win_rate:.1f}%")
else:
    print("\nNo resolved markets found in dataset.")

# Check for markets with close dates in the past
current_date = datetime.now(timezone.utc)
past_close_markets = []

for market in markets:
    close_date_str = market.get('close_date')
    if close_date_str:
        try:
            close_date = datetime.fromisoformat(close_date_str.replace('Z', '+00:00'))
            if close_date < current_date:
                past_close_markets.append(market)
        except (ValueError, TypeError):
            pass

print(f"\nMarkets with past close dates: {len(past_close_markets)}")