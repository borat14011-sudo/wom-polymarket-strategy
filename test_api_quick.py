#!/usr/bin/env python3
"""
Quick test of Polymarket API
"""

import os
import sys
from dotenv import load_dotenv

# Add the bot directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'POLYMARKET_TRADING_BOT'))

from polymarket_api_client import PolymarketAPIClient

# Load API credentials
load_dotenv('POLYMARKET_TRADING_BOT/.env.api')

api_key = os.getenv('POLYMARKET_API_KEY')
api_secret = os.getenv('POLYMARKET_API_SECRET')
passphrase = os.getenv('POLYMARKET_PASSPHRASE')
wallet_address = os.getenv('POLY_WALLET_ADDRESS')

print("Testing Polymarket API...")
print(f"API Key: {api_key[:20]}...")
print(f"Wallet: {wallet_address}")

if not all([api_key, api_secret, passphrase, wallet_address]):
    print("Missing credentials!")
    sys.exit(1)

# Initialize client
client = PolymarketAPIClient(api_key, api_secret, passphrase, wallet_address)

# Test public endpoints
try:
    # Test server time
    server_time = client.get_server_time()
    print(f"Server time: {server_time}")
    
    # Test markets
    markets = client.get_markets(limit=3)
    data = markets.get('data', [])
    print(f"\nFound {len(data)} markets")
    for i, market in enumerate(data[:2]):
        print(f"{i+1}. {market.get('question', 'Unknown')[:60]}...")
        print(f"   Active: {market.get('active')}, Closed: {market.get('closed')}")
        print(f"   Accepting orders: {market.get('accepting_orders')}")
        
except Exception as e:
    print(f"Error: {e}")