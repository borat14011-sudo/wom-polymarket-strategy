"""
Polymarket API Connection Test

Purpose: Verify API credentials work before executing real trades.

What it does:
1. Load API credentials from .env.api
2. Make test API calls (get balance, list markets, get specific market)
3. Report success/failure
4. Show what the API returns

Usage:
    python test_api_connection.py

Requirements:
    - .env.api file with POLYMARKET_API_KEY, POLYMARKET_API_SECRET, POLYMARKET_PASSPHRASE
    - polymarket_api_client module
    - python-dotenv
"""

import os
from dotenv import load_dotenv
from polymarket_api_client import PolymarketAPIClient

# Load API credentials from .env.api
load_dotenv('.env.api')

api_key = os.getenv('POLYMARKET_API_KEY')
api_secret = os.getenv('POLYMARKET_API_SECRET')
passphrase = os.getenv('POLYMARKET_PASSPHRASE')

print("Testing Polymarket API Connection...")
print("=" * 50)

# Check if credentials are loaded
if not api_key or not api_secret or not passphrase:
    print("❌ Missing API credentials!")
    print("Please ensure .env.api file exists with:")
    print("  - POLYMARKET_API_KEY")
    print("  - POLYMARKET_API_SECRET")
    print("  - POLYMARKET_PASSPHRASE")
    exit(1)

# Initialize API client
client = PolymarketAPIClient(api_key, api_secret, passphrase)

# Test 1: Get balance
try:
    balance = client.get_balance()
    print(f"✅ Balance: ${balance}")
except Exception as e:
    print(f"❌ Balance check failed: {e}")

# Test 2: List markets
try:
    markets = client.get_markets()
    print(f"✅ Found {len(markets)} markets")
except Exception as e:
    print(f"❌ Markets fetch failed: {e}")

# Test 3: Get specific market
try:
    market = client.get_market('microstrategy-500k-btc-dec-31')
    print(f"✅ MSTR Market: {market}")
except Exception as e:
    print(f"❌ Market fetch failed: {e}")

print("=" * 50)
print("API Test Complete")
