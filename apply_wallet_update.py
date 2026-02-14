#!/usr/bin/env python3
"""
Apply wallet update with private key
Usage: python apply_wallet_update.py <private_key>
"""

import sys
import os
import re

def update_env_file(file_path, wallet_address, private_key=None):
    """Update .env file with new wallet and optional private key"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    updated = False
    new_lines = []
    
    for line in lines:
        # Update wallet address
        if line.strip().startswith('POLY_WALLET_ADDRESS='):
            new_lines.append(f'POLY_WALLET_ADDRESS={wallet_address}\n')
            updated = True
        elif line.strip().startswith('WALLET_ADDRESS='):
            new_lines.append(f'WALLET_ADDRESS={wallet_address}\n')
            updated = True
        elif line.strip().startswith('wallet_address='):
            new_lines.append(f'wallet_address="{wallet_address}"\n')
            updated = True
        # Update private key if provided
        elif private_key and line.strip().startswith('PRIVATE_KEY='):
            new_lines.append(f'PRIVATE_KEY={private_key}\n')
            updated = True
        elif private_key and line.strip().startswith('private_key='):
            new_lines.append(f'private_key="{private_key}"\n')
            updated = True
        else:
            new_lines.append(line)
    
    if updated:
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
        print(f"Updated: {file_path}")
        return True
    else:
        print(f"No changes: {file_path}")
        return False

def update_py_file(file_path, wallet_address, private_key=None):
    """Update Python file with new wallet"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update wallet address patterns
    old_wallet = "0xb354e25623617a24164639F63D8b731250AC92d8"
    
    new_content = content.replace(old_wallet, wallet_address)
    
    # Update private key if provided
    if private_key:
        old_key = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
        new_content = new_content.replace(old_key, private_key)
    
    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Updated: {file_path}")
        return True
    else:
        print(f"No changes: {file_path}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python apply_wallet_update.py <private_key>")
        print("Example: python apply_wallet_update.py 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        sys.exit(1)
    
    private_key = sys.argv[1]
    wallet_address = "0x9e24439aC551E757E8d578614336b4e482aC9EEF"
    
    print("="*60)
    print("APPLYING WALLET UPDATE")
    print("="*60)
    print(f"Wallet: {wallet_address}")
    print(f"Private key: {private_key[:20]}...")
    
    # Verify private key format
    if not private_key.startswith('0x') or len(private_key) != 66:
        print(f"Warning: Private key format may be incorrect")
        print(f"Expected: 0x + 64 hex characters")
        print(f"Got: {len(private_key)} characters")
    
    # Files to update
    files = [
        ("POLYMARKET_TRADING_BOT/.env.api", update_env_file),
        ("POLYMARKET_TRADING_BOT/.env", update_env_file),
        ("polymarket_bot/config.py", update_py_file),
        ("agent_manager.py", update_py_file),
        ("execute_pending_trade.py", update_py_file),
        ("ready_to_trade.py", update_py_file),
        ("working_test_trade.py", update_py_file),
        ("test_trade_execution.py", update_py_file),
    ]
    
    print("\nUpdating files...")
    updated_count = 0
    
    for file_path, update_func in files:
        try:
            if update_func(file_path, wallet_address, private_key):
                updated_count += 1
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
    
    print(f"\nUpdated {updated_count} files")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Test new configuration:")
    print("   python test_new_wallet.py")
    print("\n2. Execute test trade:")
    print("   python execute_first_trade.py")
    print("\n3. Start automated trading:")
    print("   python run_agent_manager.py")
    
    # Create test script
    with open('test_new_wallet.py', 'w') as f:
        f.write(f'''#!/usr/bin/env python3
"""
Test new wallet configuration
"""

from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

private_key = "{private_key}"
wallet_address = "{wallet_address}"

print("Testing new wallet...")

# Verify
account = Account.from_key(private_key)
if account.address.lower() == wallet_address.lower():
    print(f"✅ Wallet verified: {{wallet_address}}")
else:
    print(f"❌ Mismatch: {{account.address}} != {{wallet_address}}")
    exit(1)

# Test API
try:
    client = ClobClient("https://clob.polymarket.com", chain_id=POLYGON, key=private_key)
    server_time = client.get_server_time()
    print(f"✅ API connected: server time {{server_time}}")
    
    # Try to get markets
    markets = client.get_markets()
    print(f"✅ Market data accessible: {{len(markets)}} markets")
    
    print("\\n✅ ALL TESTS PASSED!")
    print("Wallet is ready for trading!")
    
except Exception as e:
    print(f"❌ API test failed: {{e}}")
''')
    
    print(f"\n✅ Created test script: test_new_wallet.py")
    print("\n✅ Configuration update complete!")
    print("✅ Ready for trading!")

if __name__ == "__main__":
    main()