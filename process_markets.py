import json
import re

# Load data
with open('markets_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter active markets with volume > $100K
filtered = [m for m in data if m.get('active') == True and m.get('volumeNum', 0) > 100000]

def get_market_type(market):
    '''Categorize market by type based on question and category'''
    q = market.get('question', '').lower()
    events = market.get('events', [])
    
    # Get category from events if available
    event_cat = ''
    if events and len(events) > 0:
        event_cat = events[0].get('category', '').lower()
    
    # Check keywords for each category
    politics_keywords = ['election', 'trump', 'biden', 'vote', 'president', 'congress', 'senate', 
                         'political', 'governor', 'mayor', 'inaugurated', 'white house', 'democrat', 
                         'republican', 'primary', 'house of representatives', 'ballot', 'poll', 
                         'approval rating', 'nomination']
    
    crypto_keywords = ['crypto', 'bitcoin', 'btc', 'ethereum', 'eth', 'token', 'nft', 'defi', 
                       'blockchain', 'altcoin', 'binance', 'coinbase', 'solana', 'cardano', 
                       'cryptocurrency', 'ether', 'satoshi', 'wallet', 'mining', 'halving']
    
    sports_keywords = ['super bowl', 'nba', 'nfl', 'mlb', 'soccer', 'football', 'basketball', 
                       'tennis', 'golf', 'olympics', 'fifa', 'world cup', 'champions', 'ufc', 
                       'mma', 'boxing', 'hockey', 'nhl', 'premier league', 'la liga', 'mls']
    
    entertainment_keywords = ['oscar', 'grammy', 'emmy', 'movie', 'film', 'actor', 'actress', 
                              'director', 'album', 'song', 'music', 'celebrity', 'kardashian', 
                              'kanye', 'taylor swift', 'beyonce', 'album of the year', 'tour']
    
    science_keywords = ['spacex', 'elon', 'ai', 'artificial intelligence', 'space', 'mars', 
                        'science', 'weather', 'climate', 'nasa', 'research', 'fda', 'vaccine', 
                        'covid', 'pandemic', 'falcon', 'rocket', 'satellite']
    
    # Check event category first
    if 'politics' in event_cat or 'political' in event_cat:
        return 'political'
    elif 'crypto' in event_cat or 'finance' in event_cat:
        return 'crypto'
    elif 'sports' in event_cat:
        return 'sports'
    elif 'entertainment' in event_cat:
        return 'entertainment'
    elif 'science' in event_cat:
        return 'science'
    
    # Then check keywords in question
    if any(kw in q for kw in politics_keywords):
        return 'political'
    elif any(kw in q for kw in crypto_keywords):
        return 'crypto'
    elif any(kw in q for kw in sports_keywords):
        return 'sports'
    elif any(kw in q for kw in entertainment_keywords):
        return 'entertainment'
    elif any(kw in q for kw in science_keywords):
        return 'science'
    else:
        return 'other'

# Process markets
results = []
for m in filtered:
    events = m.get('events', [])
    event_category = events[0].get('category', 'Uncategorized') if events else 'Uncategorized'
    
    market_data = {
        'id': m.get('id'),
        'question': m.get('question'),
        'category': event_category,
        'volume': m.get('volume'),
        'volumeNum': m.get('volumeNum'),
        'liquidity': m.get('liquidity'),
        'liquidityNum': m.get('liquidityNum'),
        'resolution_date': m.get('endDate'),
        'endDateIso': m.get('endDateIso'),
        'market_type': get_market_type(m),
        'slug': m.get('slug')
    }
    results.append(market_data)

# Sort by volume descending
results.sort(key=lambda x: x.get('volumeNum', 0), reverse=True)

# Save to file
with open('data_snapshot_1.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

# Print summary
print('Markets with volume > $100K:', len(results))
print('\nBreakdown by type:')
types_count = {}
for r in results:
    t = r['market_type']
    types_count[t] = types_count.get(t, 0) + 1
for t, c in sorted(types_count.items(), key=lambda x: -x[1]):
    print('  ' + t + ': ' + str(c))

print('\nTop 10 by volume:')
for r in results[:10]:
    vol_str = '{:,.0f}'.format(r['volumeNum'])
    q = r['question'][:60] if len(r['question']) > 60 else r['question']
    print('  $' + vol_str + ' - ' + q + ' (' + r['market_type'] + ')')
