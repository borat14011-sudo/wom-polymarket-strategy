#!/usr/bin/env python3
"""
Update configuration with correct private key
"""

import os
import re

def update_file(file_path, pattern, replacement):
    """Update a file with new wallet/private key"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update content
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
    else:
        print(f"File not found: {file_path}")
        return False

print("="*60)
print("CONFIGURATION UPDATER")
print("="*60)

# Configuration
OLD_WALLET = "0xb354e25623617a24164639F63D8b731250AC92d8"
NEW_WALLET = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"

print(f"Old wallet: {OLD_WALLET}")
print(f"New wallet: {NEW_WALLET}")

print("\nFiles to update:")
print("1. POLYMARKET_TRADING_BOT/.env.api")
print("2. POLYMARKET_TRADING_BOT/.env")
print("3. polymarket_bot/config.py")
print("4. agent_manager.py")
print("5. All trading scripts")

print("\n" + "="*60)
print("READY FOR EXECUTION")
print("="*60)
print("When private key received:")
print("1. Run: python apply_wallet_update.py <private_key>")
print("2. Test: python test_new_wallet.py")
print("3. Trade: python execute_first_trade.py")

print("\nExample command:")
print('python apply_wallet_update.py "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"')

print("\n" + "="*60)
print("GET PRIVATE KEY NOW")
print("="*60)
print("URL: https://reveal.magic.link")
print("Email: borat14011@gmail.com")
print("Wallet: 0x9e24439aC551E757E8d578614336b4e482aC9EEF")
print("\nSend screenshot with private key!")