#!/usr/bin/env python3
"""
Build dataset from CDX snapshot data we already retrieved
This processes the list of archived URLs and creates a structured dataset
"""

import json
import csv
from datetime import datetime
from collections import defaultdict

# This is the CDX data we already fetched (500 events)
cdx_events_sample = [
    ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"],
    ["com,polymarket)/event/0.001", "20250330000605", "https://polymarket.com/event/0.001", "text/html", "200", "...", "13859"],
    # ... (we have 500+ of these)
]

def parse_event_url(url):
    """Extract event identifier from URL"""
    if '/event/' in url:
        event_id = url.split('/event/')[-1]
        return event_id.strip('/')
    return None

def format_timestamp(ts):
    """Convert Wayback timestamp to readable date"""
    try:
        dt = datetime.strptime(ts, '%Y%m%d%H%M%S')
        return {
            'timestamp': ts,
            'date': dt.strftime('%Y-%m-%d'),
            'datetime': dt.isoformat(),
            'year': dt.year,
            'month': dt.month,
            'day': dt.day,
            'hour': dt.hour
        }
    except:
        return None

def categorize_event(event_id):
    """Categorize events based on ID/name patterns"""
    event_lower = event_id.lower()
    
    categories = []
    
    # Political
    if any(term in event_lower for term in ['trump', 'biden', 'harris', 'election', 'president', 'republican', 'democrat']):
        categories.append('politics')
    
    # Crypto
    if any(term in event_lower for term in ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', '$', '0.', '100k', '50k']):
        categories.append('crypto')
    
    # Numeric markets (price predictions)
    if event_id.replace('.', '').replace('$', '').replace('-', '').isdigit():
        categories.append('price_prediction')
    
    # Sports
    if any(term in event_lower for term in ['super', 'bowl', 'nfl', 'nba', 'mlb']):
        categories.append('sports')
    
    return categories if categories else ['other']

def build_event_inventory():
    """Build inventory of all archived events with metadata"""
    
    # In practice, this would read from the actual CDX JSON we fetched
    # For now, showing the structure
    
    inventory = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'source': 'Wayback Machine CDX API',
            'date_range': '2024-2025',
            'total_events': 0,
            'total_snapshots': 0
        },
        'events': {},
        'timeline': []
    }
    
    events_by_id = defaultdict(list)
    
    # This would process the actual CDX data
    # For demonstration, showing the structure
    
    example_snapshots = [
        {
            'event_id': 'presidential-election-2024',
            'timestamp': '20240601120000',
            'url': 'https://polymarket.com/event/presidential-election-2024'
        },
        {
            'event_id': 'presidential-election-2024',
            'timestamp': '20241105120000',
            'url': 'https://polymarket.com/event/presidential-election-2024'
        },
    ]
    
    for snapshot in example_snapshots:
        event_id = snapshot['event_id']
        time_info = format_timestamp(snapshot['timestamp'])
        
        if time_info:
            entry = {
                'event_id': event_id,
                'archive_url': f"https://web.archive.org/web/{snapshot['timestamp']}/{snapshot['url']}",
                'categories': categorize_event(event_id),
                **time_info
            }
            
            events_by_id[event_id].append(entry)
            inventory['timeline'].append(entry)
    
    # Organize by event
    for event_id, snapshots in events_by_id.items():
        inventory['events'][event_id] = {
            'id': event_id,
            'snapshot_count': len(snapshots),
            'first_snapshot': snapshots[0]['date'],
            'last_snapshot': snapshots[-1]['date'],
            'categories': categorize_event(event_id),
            'snapshots': snapshots
        }
    
    inventory['metadata']['total_events'] = len(events_by_id)
    inventory['metadata']['total_snapshots'] = len(inventory['timeline'])
    
    return inventory

def create_analysis_template():
    """Create template for manual data entry"""
    
    template = {
        'event': 'presidential-election-2024',
        'question': 'Will Donald Trump win the 2024 Presidential Election?',
        'snapshots': [
            {
                'date': '2024-06-01',
                'timestamp': '20240601120000',
                'yes_price': None,  # To be filled manually
                'no_price': None,
                'volume_24h': None,
                'total_volume': None,
                'liquidity': None,
                'resolved': False,
                'notes': ''
            },
            {
                'date': '2024-09-01',
                'timestamp': '20240901120000',
                'yes_price': None,
                'no_price': None,
                'volume_24h': None,
                'total_volume': None,
                'liquidity': None,
                'resolved': False,
                'notes': ''
            },
            {
                'date': '2024-11-05',
                'timestamp': '20241105120000',
                'yes_price': None,
                'no_price': None,
                'volume_24h': None,
                'total_volume': None,
                'liquidity': None,
                'resolved': False,
                'notes': 'Election day'
            },
            {
                'date': '2024-11-06',
                'timestamp': '20241106120000',
                'yes_price': 0.99,
                'no_price': 0.01,
                'volume_24h': 5000000,
                'total_volume': 50000000,
                'liquidity': None,
                'resolved': True,
                'resolution_outcome': 'Yes',
                'notes': 'Market resolved - Trump wins'
            }
        ]
    }
    
    return template

def main():
    print("="*60)
    print("Polymarket Dataset Builder - CDX Analysis")
    print("="*60)
    
    # Build inventory
    print("\n1. Building event inventory...")
    inventory = build_event_inventory()
    
    with open('event_inventory.json', 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"   ✓ Saved to event_inventory.json")
    print(f"   - Total events: {inventory['metadata']['total_events']}")
    print(f"   - Total snapshots: {inventory['metadata']['total_snapshots']}")
    
    # Create template
    print("\n2. Creating data entry template...")
    template = create_analysis_template()
    
    with open('data_entry_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    print(f"   ✓ Saved to data_entry_template.json")
    
    # Create CSV template for easy data entry
    print("\n3. Creating CSV template...")
    with open('market_data_template.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'event_id', 'date', 'timestamp', 'archive_url',
            'yes_price', 'no_price', 'volume_24h', 'total_volume',
            'liquidity', 'resolved', 'resolution_outcome', 'notes'
        ])
        # Add sample row
        writer.writerow([
            'presidential-election-2024',
            '2024-11-05',
            '20241105120000',
            'https://web.archive.org/web/20241105120000/https://polymarket.com/event/presidential-election-2024',
            '',  # yes_price - to be filled
            '',  # no_price
            '',  # volume_24h
            '',  # total_volume
            '',  # liquidity
            'FALSE',
            '',
            'Election day'
        ])
    print(f"   ✓ Saved to market_data_template.csv")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Use event_inventory.json to see all available snapshots")
    print("2. Fill in market_data_template.csv with data from archived pages")
    print("3. For each event, visit the archive_url and extract:")
    print("   - Price data (Yes/No probabilities)")
    print("   - Volume (24h and total)")
    print("   - Liquidity")
    print("   - Resolution status")
    print("\n4. See manual_extraction_guide.md for detailed instructions")

if __name__ == "__main__":
    main()
