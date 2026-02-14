import json

# Try to load the full file
try:
    with open('polymarket_latest.json', 'r', encoding='utf-8', errors='ignore') as f:
        # Read in chunks to handle large file
        data = ''
        while True:
            chunk = f.read(100000)
            if not chunk:
                break
            data += chunk
            
        # Find where JSON ends
        end_pos = data.rfind(']')
        if end_pos > 0:
            data = data[:end_pos+1]
            data = '{"markets":' + data + '}'
            
        parsed = json.loads(data)
        markets = parsed.get('markets', [])
        print(f'Successfully parsed {len(markets)} markets')
        
        # Check first few markets
        for i, m in enumerate(markets[:5]):
            print(f'\nMarket {i}:')
            print(f'  ID: {m.get("id", "N/A")}')
            print(f'  Question: {m.get("question", "N/A")[:80]}...')
            print(f'  Active: {m.get("active", "N/A")}')
            print(f'  Outcomes: {m.get("outcomes", [])}')
            print(f'  Prices: {m.get("outcomePrices", [])}')
            print(f'  Volume: {m.get("volumeNum", "N/A")}')
            
        # Count active markets
        active = [m for m in markets if m.get('active')]
        print(f'\nActive markets: {len(active)}')
        
        # Check price distribution
        price_counts = {'<0.3': 0, '0.3-0.7': 0, '>0.7': 0, '0.9-0.98': 0}
        for m in active:
            prices = m.get('outcomePrices', [])
            outcomes = m.get('outcomes', [])
            if len(prices) >= 2 and len(outcomes) >= 2:
                try:
                    yes_price = float(prices[0]) if outcomes[0] == 'Yes' else float(prices[1])
                    if yes_price < 0.3:
                        price_counts['<0.3'] += 1
                    elif yes_price < 0.7:
                        price_counts['0.3-0.7'] += 1
                    elif yes_price < 0.9:
                        price_counts['>0.7'] += 1
                    elif yes_price <= 0.98:
                        price_counts['0.9-0.98'] += 1
                except:
                    pass
        
        print('\nPrice distribution:')
        for range_name, count in price_counts.items():
            print(f'  {range_name}: {count}')
            
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()