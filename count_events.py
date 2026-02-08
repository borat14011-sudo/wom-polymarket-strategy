with open('polymarket-monitor/historical-data-scraper/data/polymarket_complete.json') as f:
    content = f.read()
    count = content.count('"question"')
    print(f'Estimated events: {count:,}')
    print(f'File size: {len(content):,} bytes')
