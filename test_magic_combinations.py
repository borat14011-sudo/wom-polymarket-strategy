#!/usr/bin/env python3
"""
Test both wallet combinations with Magic authentication
"""

print("="*60)
print("TEST MAGIC WALLET COMBINATIONS")
print("="*60)

# Two wallets we have
WALLET_A = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"  # Has $10.41 in Polymarket
WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"  # Private key we have

PRIVATE_KEY_B = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
EMAIL = "borat14011@gmail.com"

print(f"Wallet A (Polymarket): {WALLET_A}")
print(f"Wallet B (Private key): {WALLET_B}")
print(f"Email: {EMAIL}")
print(f"Private key for Wallet B: {PRIVATE_KEY_B[:20]}...")

print("\n" + "="*60)
print("SCENARIOS TO TEST")
print("="*60)

print("1. Wallet A + Email (Polymarket account)")
print("   - Has $10.41 USDC")
print("   - Need private key or Magic login")
print("   - Try Magic code login")

print("\n2. Wallet B + Email (Different wallet)")
print("   - We have private key")
print("   - May need to fund with USDC")
print("   - Can create new Polymarket account")

print("\n3. Wallet B + Different email")
print("   - Private key might be associated with different email")
print("   - Need to check Magic.link associations")

print("\n" + "="*60)
print("TESTING APPROACH")
print("="*60)

print("Step 1: Try Magic code login for Wallet A")
print("   - Go to https://polymarket.com")
print("   - Click 'Connect Wallet'")
print("   - Choose 'Email' option")
print("   - Enter: borat14011@gmail.com")
print("   - Check email for Magic code")
print("   - Login and see which wallet connects")

print("\nStep 2: Try private key login for Wallet B")
print("   - Go to https://polymarket.com")
print("   - Click 'Connect Wallet'")
print("   - Choose 'Private Key' or 'Show all options'")
print("   - Enter private key for Wallet B")
print("   - See if it connects")

print("\nStep 3: Check Magic.link dashboard")
print("   - Go to https://dashboard.magic.link")
print("   - Login with borat14011@gmail.com")
print("   - See all associated wallets")

print("\n" + "="*60)
print("PRACTICAL TEST")
print("="*60)

print("Let me test Wallet B with private key first...")

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

# Test Wallet B connectivity
print(f"\nTesting Wallet B ({WALLET_B})...")
try:
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=PRIVATE_KEY_B)
    server_time = client.get_server_time()
    print(f"OK: Wallet B can connect to Polymarket API")
    
    # Try to get API keys (requires registration)
    try:
        api_keys = client.get_api_keys()
        print(f"OK: Wallet B has API keys")
    except Exception as e:
        print(f"Note: Wallet B needs API keys: {e}")
        
except Exception as e:
    print(f"Wallet B connection failed: {e}")

print("\n" + "="*60)
print("RECOMMENDED ACTION")
print("="*60)
print("1. FIRST: Try Magic code login for Wallet A")
print("   - This is the wallet with $10.41")
print("   - Use email: borat14011@gmail.com")
print("   - Get Magic code from email")
print("   - Login and check wallet address")

print("\n2. If Wallet A connects:")
print("   - We're in! Use the $10.41")
print("   - Need to get private key for Wallet A")
print("   - Or use Magic session for trading")

print("\n3. If Wallet A doesn't connect:")
print("   - Fund Wallet B with $10")
print("   - Create new Polymarket account")
print("   - Use existing bot setup")

print("\n" + "="*60)
print("QUICKEST PATH TO TRADING")
print("="*60)
print("Option 1: Magic login to Wallet A (if it works)")
print("   - Use existing $10.41")
print("   - Need to figure out auth method")

print("Option 2: Fund Wallet B ($10 transfer)")
print("   - Send USDC to {WALLET_B}")
print("   - Use existing bot configuration")
print("   - Start trading immediately")

print("\n" + "="*60)
print("IMMEDIATE NEXT STEP")
print("="*60)
print("Please try Magic code login:")
print("1. Go to https://polymarket.com")
print("2. Click 'Connect Wallet'")
print("3. Choose 'Email'")
print("4. Enter: borat14011@gmail.com")
print("5. Check email for Magic code")
print("6. Login and tell me which wallet appears")
print("\nThis will tell us which wallet is associated with the email!")