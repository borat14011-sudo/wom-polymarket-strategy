#!/usr/bin/env python3
"""
Check Wallet B balance
"""

import requests
import time

WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"

print("CHECKING WALLET B BALANCE")
print("="*60)
print(f"Wallet: {WALLET_B}")
print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "="*60)
print("METHOD 1: Gamma API")
print("="*60)

try:
    # Gamma API for wallet info
    gamma_url = f"https://gamma-api.polymarket.com/accounts/{WALLET_B}"
    response = requests.get(gamma_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: Found wallet on Gamma API")
        
        # Extract balance info
        if 'balances' in data:
            balances = data['balances']
            print(f"Balances: {balances}")
            
            # Look for USDC
            for balance in balances:
                if balance.get('token') == 'USDC':
                    amount = float(balance.get('amount', 0))
                    print(f"USDC Balance: ${amount:.2f}")
                    if amount >= 10:
                        print("✅ FUNDED! Ready to trade!")
                    else:
                        print(f"❌ Insufficient: ${amount:.2f} (need $10)")
        else:
            print(f"No balance data found")
            
    elif response.status_code == 404:
        print(f"Wallet not found on Gamma API (404)")
        print("This is normal for new/unfunded wallets")
    else:
        print(f"Gamma API: {response.status_code} - {response.text[:100]}")
        
except Exception as e:
    print(f"Gamma API error: {e}")

print("\n" + "="*60)
print("METHOD 2: CLOB API")
print("="*60)

try:
    # CLOB API for balance
    clob_url = f"https://clob.polymarket.com/balances?address={WALLET_B}"
    response = requests.get(clob_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"SUCCESS: CLOB API returned data")
        
        if data:
            print(f"Balance data: {data}")
            # Look for USDC
            for item in data:
                if item.get('token') == 'USDC':
                    amount = float(item.get('amount', 0))
                    print(f"USDC Balance: ${amount:.2f}")
                    if amount >= 10:
                        print("✅ FUNDED! Ready to trade!")
                    else:
                        print(f"❌ Insufficient: ${amount:.2f} (need $10)")
        else:
            print(f"No balance data (empty array)")
            
    elif response.status_code == 404:
        print(f"Wallet not found on CLOB API (404)")
    else:
        print(f"CLOB API: {response.status_code} - {response.text[:100]}")
        
except Exception as e:
    print(f"CLOB API error: {e}")

print("\n" + "="*60)
print("METHOD 3: Polygon Scan")
print("="*60)

try:
    # Check PolygonScan for USDC transactions
    polygonscan_url = f"https://api.polygonscan.com/api"
    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': WALLET_B,
        'contractaddress': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',  # USDC on Polygon
        'page': 1,
        'offset': 10,
        'sort': 'desc',
        'apikey': 'YourApiKeyToken'  # Would need actual API key
    }
    
    print("PolygonScan check requires API key")
    print("Skipping - would need paid API key")
    
except Exception as e:
    print(f"PolygonScan error: {e}")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("1. Gamma API is most reliable for Polymarket balances")
print("2. If wallet shows 404, it's unfunded or new")
print("3. Check your transaction on PolygonScan manually")

print("\n" + "="*60)
print("NEXT STEP")
print("="*60)
print("Let me check the balance using the trading bot's method...")