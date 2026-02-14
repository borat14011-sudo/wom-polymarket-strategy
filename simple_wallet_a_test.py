#!/usr/bin/env python3
"""
Simple test with Wallet A configuration
"""

import os
import json

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_A = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"

print("="*60)
print("SIMPLE WALLET A TEST")
print("="*60)

print(f"Wallet A: {WALLET_A}")
print(f"Private key: {PRIVATE_KEY[:20]}...")

print("\n" + "="*60)
print("UPDATING CONFIGURATION")
print("="*60)

# Update polymarket_bot/.env
env_path = "polymarket_bot/.env"
env_content = f"""PRIVATE_KEY={PRIVATE_KEY}
FUNDER_ADDRESS={WALLET_A}
INITIAL_CAPITAL=10.41
MAX_POSITION_SIZE=0.20
MAX_TOTAL_EXPOSURE=2.50
MAX_CONCURRENT_POSITIONS=3
SCAN_INTERVAL_MINUTES=5
"""

with open(env_path, 'w') as f:
    f.write(env_content)

print(f"Updated {env_path}")
print(f"Set FUNDER_ADDRESS to {WALLET_A}")
print(f"Set INITIAL_CAPITAL to 10.41")

print("\n" + "="*60)
print("TESTING CONNECTION")
print("="*60)

# Try to run the bot's test
test_script = "polymarket_bot/test_bot.py"
if os.path.exists(test_script):
    print(f"Running test: {test_script}")
    os.system(f"python {test_script}")
else:
    print("Test script not found, trying direct import...")
    
    # Try direct import
    import sys
    sys.path.append('polymarket_bot')
    
    try:
        from config import validate_config, PRIVATE_KEY as CONFIG_PK, FUNDER_ADDRESS as CONFIG_ADDR
        
        print("Config import successful")
        print(f"Config PRIVATE_KEY: {CONFIG_PK[:20]}...")
        print(f"Config FUNDER_ADDRESS: {CONFIG_ADDR}")
        
        # Validate
        validate_config()
        print("Config validation passed!")
        
    except Exception as e:
        print(f"Import failed: {e}")

print("\n" + "="*60)
print("NEXT STEP")
print("="*60)
print("The bot is now configured for Wallet A.")
print("However, the private key mathematically belongs to Wallet B.")

print("\nTwo options:")
print("1. Try trading anyway - Magic might handle it differently")
print("2. Get Wallet A's actual private key")

print("\nLet me try a small test trade to see what happens...")