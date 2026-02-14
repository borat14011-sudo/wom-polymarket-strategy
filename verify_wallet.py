#!/usr/bin/env python3
"""
Verify wallet address and private key match
"""

from eth_account import Account

# Provided credentials
provided_wallet = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"
provided_private_key = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("="*60)
print("WALLET VERIFICATION")
print("="*60)

# Generate wallet from private key
try:
    account = Account.from_key(provided_private_key)
    generated_wallet = account.address
    
    print(f"Provided wallet:    {provided_wallet}")
    print(f"Generated wallet:   {generated_wallet}")
    print(f"Match:              {generated_wallet.lower() == provided_wallet.lower()}")
    
    if generated_wallet.lower() != provided_wallet.lower():
        print("\n" + "!"*60)
        print("WARNING: Private key does NOT match wallet address!")
        print("!"*60)
        print("\nPossible issues:")
        print("1. Private key is incorrect for this wallet")
        print("2. Wallet address is incorrect")
        print("3. There's a typo in either value")
        
        print("\nThe private key generates wallet: 0xb354e25623617a24164639F63D8b731250AC92d8")
        print("But you provided wallet:         0x9e24439aC551E757E8d578614336b4e482aC9EEF")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. Log into https://polymarket.com")
print("2. Check which wallet has funds (USDC balance)")
print("3. For the correct wallet, get private key from:")
print("   https://reveal.magic.link/polymarket")
print("4. Update credentials with matching pair")