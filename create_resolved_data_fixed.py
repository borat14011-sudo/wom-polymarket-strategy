import json
from datetime import datetime

# Load the resolved markets (handle BOM)
with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    raw_markets = json.load(f)

print(f"Loaded {len(raw_markets)} raw markets")

# Transform to backtest format
fixed_markets = []
for m in raw_markets:
    # Parse final prices
    final_prices_str = m.get('final_prices', '')
    outcome_prices = [0, 0]
    winner = m.get('winner', '')
    
    if final_prices_str:
        parts = final_prices_str.split('|')
        if len(parts) == 2:
            try:
                outcome_prices = [float(parts[0]), float(parts[1])]
            except:
                # Infer from winner
                if winner == 'Yes':
                    outcome_prices = [1, 0]
                elif winner == 'No':
                    outcome_prices = [0, 1]
    else:
        # Infer from winner
        if winner == 'Yes':
            outcome_prices = [1, 0]
        elif winner == 'No':
            outcome_prices = [0, 1]
    
    # Parse volume
    volume = 0
    try:
        volume = float(m.get('volume_usd', 0))
    except:
        pass
    
    # Parse dates
    created_at = m.get('created_time', '')
    end_date = m.get('event_end_date', '')
    
    # Clean up created_at format
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            created_at = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            created_at = '2025-01-01T00:00:00Z'
    else:
        created_at = '2025-01-01T00:00:00Z'
    
    # Clean up end_date format
    if end_date:
        try:
            if 'T' not in end_date:
                end_date = end_date + 'T00:00:00Z'
            elif not end_date.endswith('Z') and '+' not in end_date:
                end_date = end_date + 'Z'
        except:
            end_date = '2025-12-31T00:00:00Z'
    else:
        end_date = '2025-12-31T00:00:00Z'
    
    fixed_market = {
        'id': m.get('market_id', ''),
        'question': m.get('question', ''),
        'closed': m.get('closed', 'True').lower() == 'true',
        'outcome_prices': outcome_prices,
        'winner': winner,
        'volume': volume,
        'created_at': created_at,
        'end_date': end_date,
        'event_title': m.get('event_title', ''),
        'event_slug': m.get('event_slug', ''),
        'condition_id': m.get('condition_id', '')
    }
    
    fixed_markets.append(fixed_market)

print(f"Transformed {len(fixed_markets)} markets")

# Save as RESOLVED_DATA_FIXED.json
output = {
    'metadata': {
        'created_at': datetime.now().isoformat(),
        'source': 'polymarket_resolved_markets.json',
        'total_markets': len(fixed_markets),
        'description': 'Resolved markets data for backtesting - FIXED format'
    },
    'markets': fixed_markets
}

with open('RESOLVED_DATA_FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"Saved RESOLVED_DATA_FIXED.json with {len(fixed_markets)} markets")

# Verify a few markets
print("\nSample markets:")
for m in fixed_markets[:3]:
    print(f"  - {m['question'][:60]}...")
    print(f"    Winner: {m['winner']}, Prices: {m['outcome_prices']}, Volume: ${m['volume']:,.0f}")
