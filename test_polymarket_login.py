#!/usr/bin/env python3
"""
Test if we can use the private key to interact with Polymarket
"""

from eth_account import Account
import requests
import json

PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"

print("TESTING POLYMARKET LOGIN WITH PRIVATE KEY")
print("="*60)

# Derive wallet address
acc = Account.from_key(PRIVATE_KEY)
wallet_address = acc.address
print(f"Wallet address: {wallet_address}")

print("\n" + "="*60)
print("METHOD 1: Direct CLOB API Authentication")
print("="*60)

try:
    # Try to create a signature for authentication
    from web3 import Web3
    
    # Create a test message to sign
    message = "Polymarket authentication test"
    signed_message = acc.sign_message(message)
    
    print(f"Message: {message}")
    print(f"Signature: {signed_message.signature.hex()}")
    print(f"Can sign messages with this private key")
    
except ImportError:
    print("web3 not installed")
except Exception as e:
    print(f"Signing error: {e}")

print("\n" + "="*60)
print("METHOD 2: Check Wallet on Polygonscan")
print("="*60)

print(f"Check wallet activity on Polygonscan:")
print(f"https://polygonscan.com/address/{wallet_address}")

print("\n" + "="*60)
print("METHOD 3: Try Polymarket Website Manually")
print("="*60)

print("To test manually:")
print("1. Go to https://polymarket.com")
print("2. Click 'Connect Wallet'")
print("3. Choose 'MetaMask' or 'WalletConnect'")
print("4. Import private key: " + PRIVATE_KEY[:20] + "...")
print("5. Check if balance appears")

print("\n" + "="*60)
print("CRITICAL QUESTION")
print("="*60)
print("Which wallet has the $10.41 balance?")
print("\nPreviously we saw Wallet A had $10.41")
print("But now both show 404 on Gamma API")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("Let's try connecting to Polymarket with the private key")
print("and see which wallet appears and what balance it has.")

print("\n" + "="*60)
print("NEXT STEP")
print("="*60)
print("Can you try connecting to Polymarket with the private key?")
print("1. Go to https://polymarket.com")
print("2. Connect wallet using private key")
print("3. Tell me which wallet appears and balance")
print("\nOR")
print("\nSend $10 to the wallet that appears when you connect.")