#!/usr/bin/env python3
"""
Prepare configuration for both wallet options
"""

import os

print("="*60)
print("PREPARING BOTH WALLET OPTIONS")
print("="*60)

WALLET_A = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"  # Has $10.41
WALLET_B = "0xb354e25623617a24164639F63D8b731250AC92d8"  # We have private key
PRIVATE_KEY_B = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print(f"Wallet A: {WALLET_A}")
print(f"  - Has $10.41 in Polymarket")
print(f"  - Need private key (unknown)")
print(f"  - Magic login might work")

print(f"\nWallet B: {WALLET_B}")
print(f"  - Private key: {PRIVATE_KEY_B[:20]}...")
print(f"  - Can connect to API")
print(f"  - Needs $10 funding")

print("\n" + "="*60)
print("PREPARING CONFIGURATIONS")
print("="*60)

# Create config for Wallet A (if we get private key)
wallet_a_config = f"""# Wallet A Configuration (if we get private key)
WALLET_ADDRESS = "{WALLET_A}"
PRIVATE_KEY = "REPLACE_IF_WE_GET_IT"
BALANCE = 10.41
"""

# Create config for Wallet B (ready to use)
wallet_b_config = f"""# Wallet B Configuration (ready)
WALLET_ADDRESS = "{WALLET_B}"
PRIVATE_KEY = "{PRIVATE_KEY_B}"
BALANCE = 0.00  # Needs funding
"""

# Save both
with open('wallet_a_config.py', 'w') as f:
    f.write(wallet_a_config)
    
with open('wallet_b_config.py', 'w') as f:
    f.write(wallet_b_config)

print("Created:")
print("1. wallet_a_config.py - For Wallet A (needs private key)")
print("2. wallet_b_config.py - For Wallet B (ready, needs funds)")

print("\n" + "="*60)
print("NEXT STEPS BASED ON MAGIC TEST")
print("="*60)

print("IF Magic login shows Wallet A:")
print("1. We need private key for Wallet A")
print("2. Try reveal.magic.link again for correct wallet")
print("3. Or use Magic session authentication")

print("\nIF Magic login shows Wallet B:")
print("1. Fund Wallet B with $10 USDC")
print("2. Execute test trade immediately")
print("3. Start automated trading")

print("\nIF Magic login fails:")
print("1. Fund Wallet B with $10")
print("2. Create new Polymarket account")
print("3. Use Wallet B for trading")

print("\n" + "="*60)
print("QUICKEST PATH:")
print("="*60)
print("1. Do Magic login test (2 minutes)")
print("2. Based on result:")
print("   - If Wallet A: get its private key")
print("   - If Wallet B: fund it and trade")
print("3. Start trading within 10 minutes")

print("\n" + "="*60)
print("READY FOR ACTION")
print("="*60)
print("Please do the Magic login test NOW!")
print("Then tell me which wallet appears.")