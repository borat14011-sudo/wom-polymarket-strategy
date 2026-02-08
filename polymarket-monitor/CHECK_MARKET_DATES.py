# CHECK_MARKET_DATES.py - Verify which markets are actually open
import requests
import datetime

# Check which markets are actually still open
r = requests.get('https://gamma-api.polymarket.com/markets?active=true&closed=false', timeout=15)
markets = r.json()

now = datetime.datetime.now(datetime.timezone.utc)

print('=== CHECKING MARKET STATUS (Feb 8, 2026) ===')
print(f'Current Date: {now}')
print()

active_musk_markets = []

for market in markets:
    q = market.get('question', '').lower()
    if 'musk' in q or 'elon' in q or 'doge' in q:
        end_date_str = market.get('endDate', '')
        try:
            end_date = datetime.datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            is_open = end_date > now
            days_remaining = (end_date - now).days
            
            print(f'Market: {market.get("question")}')
            print(f'  End Date: {end_date_str}')
            print(f'  Status: {"OPEN" if is_open else "CLOSED/RESOLVED"}')
            print(f'  Days Remaining: {days_remaining}')
            
            if is_open:
                active_musk_markets.append(market)
                print('  >>> STILL TRADABLE')
            else:
                print('  >>> ALREADY CLOSED')
            print()
        except Exception as e:
            print(f'  Error parsing date: {e}')

print(f'=== SUMMARY ===')
musk_count = len([m for m in markets if 'musk' in m.get('question','').lower() or 'elon' in m.get('question','').lower()])
print(f'Total Musk Markets Found: {musk_count}')
print(f'Actually OPEN: {len(active_musk_markets)}')
print(f'Already CLOSED/RESOLVED: {musk_count - len(active_musk_markets)}')