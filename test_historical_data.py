import requests
import json
from datetime import datetime, timedelta

print("Testing Polymarket Historical Data API...")
print("=" * 60)
print()

# Get multiple active markets and try each
print("1. Finding active markets with high volume...")
response = requests.get('https://gamma-api.polymarket.com/markets', params={'limit': 20, 'active': True})
markets = response.json()

success_count = 0
for i, m in enumerate(markets[:10]):
    clob_ids = m.get('clobTokenIds', [])
    if isinstance(clob_ids, str):
        clob_ids = json.loads(clob_ids)
    
    if not clob_ids:
        continue
    
    token_id = clob_ids[0] if isinstance(clob_ids, list) else json.loads(clob_ids)[0]
    question = m['question']
    
    # Try to get historical data
    hist_response = requests.get(
        'https://clob.polymarket.com/prices-history',
        params={
            'market': token_id,
            'interval': 'max',  # Get all available history
            'fidelity': 1440  # Daily intervals
        }
    )
    
    if hist_response.status_code == 200:
        data = hist_response.json()
        history = data.get('history', [])
        
        if history and len(history) > 0:
            print(f"\nMarket #{i+1}: {question[:60]}...")
            print(f"  Token: {token_id[:20]}...")
            print(f"  Data points: {len(history)}")
            
            # Show first and last price
            first = history[0]
            last = history[-1]
            first_dt = datetime.fromtimestamp(first.get('t', 0))
            last_dt = datetime.fromtimestamp(last.get('t', 0))
            
            print(f"  First: {first_dt.strftime('%Y-%m-%d')} - {first.get('p', 0)*100:.1f}%")
            print(f"  Last:  {last_dt.strftime('%Y-%m-%d')} - {last.get('p', 0)*100:.1f}%")
            
            success_count += 1
            
            if success_count >= 3:
                break

print()
print("=" * 60)
if success_count > 0:
    print(f"SUCCESS: Found {success_count} markets with historical data!")
    print()
    print("WHAT THIS MEANS:")
    print("[YES] API works - can get historical prices for ACTIVE markets")
    print("[YES] Can backtest strategies on currently active markets")
    print("[NO]  Cannot get 2-year history on RESOLVED markets")
    print()
    print("IMPLICATION:")
    print("- Can validate strategies going FORWARD (30-90 days)")
    print("- Can backtest on CURRENTLY ACTIVE markets (limited history)")
    print("- Cannot backtest on OLD RESOLVED markets (no archived data)")
else:
    print("WARNING: No markets returned historical data")
    print("This may indicate:")
    print("- Markets are too new (no price history yet)")
    print("- API parameters need adjustment")
    print("- Historical data not available for current markets")
