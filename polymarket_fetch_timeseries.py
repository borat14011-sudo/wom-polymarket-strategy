#!/usr/bin/env python3
"""
Polymarket Timeseries Data Fetcher
Working script to fetch historical price data from Polymarket CLOB API
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


def get_active_markets(limit: int = 100) -> List[Dict]:
    """
    Fetch active (not closed) markets from Gamma API
    
    Returns:
        List of markets with clobTokenIds
    """
    url = f"{GAMMA_API}/markets"
    params = {
        'closed': 'false',
        'limit': limit,
        'archived': 'false'
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    
    markets = response.json()
    
    # Filter for markets with CLOB token IDs
    return [m for m in markets if m.get('clobTokenIds')]


def fetch_price_history(
    token_id: str,
    interval: str = '1w',
    fidelity: int = 60
) -> List[Dict]:
    """
    Fetch historical price data for a token
    
    Args:
        token_id: CLOB token ID
        interval: Time period (1m, 1h, 6h, 1d, 1w, max)
        fidelity: Resolution in minutes
        
    Returns:
        List of {timestamp, price} dicts
    """
    url = f"{CLOB_API}/prices-history"
    params = {
        'market': token_id,
        'interval': interval,
        'fidelity': fidelity
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    if 'history' not in data:
        return []
    
    # Convert to more readable format
    history = []
    for point in data['history']:
        history.append({
            'timestamp': datetime.fromtimestamp(point['t']),
            'timestamp_unix': point['t'],
            'price': float(point['p'])
        })
    
    return sorted(history, key=lambda x: x['timestamp'])


def main():
    """Example usage"""
    
    print("Fetching active markets...")
    markets = get_active_markets(limit=10)
    
    print(f"Found {len(markets)} active markets\n")
    
    if not markets:
        print("No active markets found")
        return
    
    # Test with first market
    market = markets[0]
    
    # Parse CLOB token IDs (they're JSON encoded)
    token_ids = json.loads(market['clobTokenIds'])
    token_id = token_ids[0]  # Get first outcome token
    
    print(f"Market: {market['question'][:80]}")
    print(f"Token ID: {token_id}")
    print(f"\nFetching price history...")
    
    # Fetch 1 week of hourly data
    history = fetch_price_history(token_id, interval='1w', fidelity=60)
    
    if not history:
        print("No price data available")
        return
    
    print(f"✓ Retrieved {len(history)} data points")
    print(f"✓ Period: {history[0]['timestamp']} to {history[-1]['timestamp']}")
    
    # Show first few points
    print("\nFirst 5 data points:")
    for point in history[:5]:
        print(f"  {point['timestamp'].isoformat()} - Price: {point['price']:.4f}")
    
    # Calculate some stats
    prices = [p['price'] for p in history]
    print(f"\nPrice statistics:")
    print(f"  Min: {min(prices):.4f}")
    print(f"  Max: {max(prices):.4f}")
    print(f"  Avg: {sum(prices)/len(prices):.4f}")
    
    # Save to file
    output = {
        'market': market['question'],
        'token_id': token_id,
        'fetched_at': datetime.now().isoformat(),
        'data_points': len(history),
        'history': history
    }
    
    with open('price_history.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n✓ Saved to price_history.json")


if __name__ == "__main__":
    main()
