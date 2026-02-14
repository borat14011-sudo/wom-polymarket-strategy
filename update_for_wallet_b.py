#!/usr/bin/env python3
"""
Update all configurations for Wallet B
"""

import os

WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("UPDATING FOR WALLET B")
print("="*60)
print(f"Wallet: {WALLET_B}")
print(f"Private key: {PRIVATE_KEY[:20]}...")

print("\n" + "="*60)
print("UPDATING CONFIGURATIONS")
print("="*60)

# 1. Update polymarket_bot/.env
bot_env = """POLYMARKET_PRIVATE_KEY=0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455
POLYMARKET_FUNDER_ADDRESS=0xb354e25623617a24164639F63D8b731250AC92d8
INITIAL_CAPITAL=10.00
MAX_POSITION_SIZE=0.20
MAX_TOTAL_EXPOSURE=2.50
MAX_CONCURRENT_POSITIONS=3
SCAN_INTERVAL_MINUTES=5
"""

with open('polymarket_bot/.env', 'w') as f:
    f.write(bot_env)
print("✅ Updated polymarket_bot/.env")

# 2. Update POLYMARKET_TRADING_BOT/.env
trading_bot_env = f"""POLY_WALLET_ADDRESS={WALLET_B}
POLY_PRIVATE_KEY={PRIVATE_KEY}
POLY_API_KEY=test
POLY_API_SECRET=test
"""

with open('POLYMARKET_TRADING_BOT/.env', 'w') as f:
    f.write(trading_bot_env)
print("✅ Updated POLYMARKET_TRADING_BOT/.env")

# 3. Update agent system configuration
agent_config = f"""# Wallet B Configuration
WALLET_ADDRESS = "{WALLET_B}"
PRIVATE_KEY = "{PRIVATE_KEY}"
INITIAL_CAPITAL = 10.00
"""

with open('wallet_b_config.py', 'w') as f:
    f.write(agent_config)
print("✅ Updated wallet_b_config.py")

print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

# Verify private key matches wallet
from eth_account import Account
acc = Account.from_key(PRIVATE_KEY)
derived = acc.address

print(f"Private key derives to: {derived}")
print(f"Wallet B address: {WALLET_B}")

if derived.lower() == WALLET_B.lower():
    print("✅ MATCH! Private key correctly configured for Wallet B")
else:
    print("❌ MISMATCH! Something wrong")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("1. YOU: Send $10 USDC to Wallet B")
print(f"   Address: {WALLET_B}")
print("   Network: Polygon")
print("   Token: USDC")

print("\n2. ME: Wait for funding confirmation")
print("   Check balance via API")
print("   Execute $0.20 test trade")
print("   Start automated trading")

print("\n" + "="*60)
print("READY FOR FUNDING")
print("="*60)
print("All systems configured for Wallet B.")
print("Send $10 USDC and trading begins immediately! 🚀")