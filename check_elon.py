import json

with open('kalshi_markets_raw.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

elon_crypto = []
for market in data:
    title = market.get('title', '').lower()
    ticker = market.get('ticker_name', '').lower()
    
    # Look for Elon, Musk, crypto, bitcoin, doge, etc.
    keywords = ['elon', 'musk', 'crypto', 'bitcoin', 'doge', 'dogecoin', 'x', 'twitter']
    if any(kw in title or kw in ticker for kw in keywords):
        weekly_change = market.get('weekly_change_pct', 0)
        if weekly_change is not None:
            elon_crypto.append({
                'ticker': market['ticker_name'],
                'title': market['title'],
                'weekly_change': weekly_change,
                'current': market['last_price'],
                'volume': market['volume']
            })

print('Elon/Crypto related markets:')
print('=' * 80)
for m in elon_crypto:
    print(f'{m["ticker"]}')
    print(f'  {m["title"][:80]}...')
    print(f'  Current: {m["current"]}c | Weekly: {m["weekly_change"]:.1f}% | Volume: {m["volume"]:,}')
    print()