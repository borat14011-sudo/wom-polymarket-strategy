import requests
import os
from pathlib import Path

BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'

print("KALSHI API STATUS CHECK")
print("=" * 50)

# 1. Test exchange status
r = requests.get(f'{BASE_URL}/exchange/status', timeout=10)
data = r.json()
print(f"Exchange Active: {data.get('exchange_active')}")
print(f"Trading Active: {data.get('trading_active')}")

# 2. Count markets
r = requests.get(f'{BASE_URL}/markets', params={'limit': 10, 'status': 'open'}, timeout=10)
data = r.json()
print(f"Sample markets fetched: {len(data.get('markets', []))}")

# 3. Check auth credentials
print("\n" + "=" * 50)
print("AUTHENTICATION CHECK")
print("=" * 50)
api_key = os.getenv('KALSHI_API_KEY_ID', '')
print(f"API Key ID set: {'YES' if api_key else 'NO'}")

key_file = Path('rsa_private_key.pem')
print(f"Private key file exists: {key_file.exists()}")

if not api_key:
    print("\n>>> MISSING: KALSHI_API_KEY_ID environment variable")
    print(">>> Get it from: https://kalshi.com/account/api")
