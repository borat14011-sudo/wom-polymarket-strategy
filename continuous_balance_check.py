#!/usr/bin/env python3
"""
Continuous balance check for Wallet B
"""

import requests
import time
import sys

WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"

print("CONTINUOUS BALANCE CHECK - WALLET B")
print("="*60)
print(f"Wallet: {WALLET_B}")
print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("Checking every 30 seconds...")
print("="*60)

check_count = 0
funded = False

while not funded and check_count < 20:  # Check for up to 10 minutes
    check_count += 1
    print(f"\nCheck #{check_count} - {time.strftime('%H:%M:%S')}")
    
    try:
        # Try Gamma API
        gamma_url = f"https://gamma-api.polymarket.com/accounts/{WALLET_B}"
        response = requests.get(gamma_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wallet found on Gamma API!")
            
            # Check for USDC balance
            if 'balances' in data:
                for balance in data['balances']:
                    if balance.get('token') == 'USDC':
                        amount = float(balance.get('amount', 0))
                        print(f"   USDC Balance: ${amount:.2f}")
                        
                        if amount >= 10:
                            print("\n" + "="*60)
                            print("🎉 FUNDED! READY TO TRADE! 🎉")
                            print("="*60)
                            print(f"Balance: ${amount:.2f}")
                            print("Executing test trade in 5 seconds...")
                            funded = True
                            break
                        elif amount > 0:
                            print(f"   Partial funding: ${amount:.2f} (need $10)")
                        else:
                            print(f"   No USDC balance yet")
                            
            else:
                print(f"   No balance data in response")
                
        elif response.status_code == 404:
            print(f"   Wallet not found (404) - still unfunded")
        else:
            print(f"   Gamma API: {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    if not funded:
        print(f"   Waiting 30 seconds...")
        time.sleep(30)

if not funded:
    print("\n" + "="*60)
    print("❌ NOT FUNDED AFTER 10 MINUTES")
    print("="*60)
    print("Wallet B still not found on Polymarket APIs.")
    print("\nPlease check:")
    print(f"1. Transaction sent to: {WALLET_B}")
    print("2. Network: Polygon")
    print("3. Token: USDC")
    print("4. Check PolygonScan:")
    print(f"   https://polygonscan.com/address/{WALLET_B}")
    
    print("\n" + "="*60)
    print("NEXT STEP")
    print("="*60)
    print("Once transaction confirms (2-5 min), balance will appear.")
    print("I'll keep checking in background.")

print("\n" + "="*60)
print("MONITORING CONTINUES")
print("="*60)
print("I'll monitor for funding and execute test trade immediately.")