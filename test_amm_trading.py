#!/usr/bin/env python3
"""
Test AMM trading on Polymarket
"""

import requests
import json
import time
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

load_dotenv('polymarket_bot/.env')

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
WALLET_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print("="*60)
print("TEST AMM TRADING ON POLYMARKET")
print("="*60)
print(f"Wallet: {WALLET_ADDRESS}")

# Step 1: Get market details
market_id = "517310"  # Trump deportation <250k
gamma_url = f"https://gamma-api.polymarket.com/markets/{market_id}"
response = requests.get(gamma_url, timeout=10)

if response.status_code == 200:
    market = response.json()
    question = market.get('question', 'Unknown')
    condition_id = market.get('conditionId')
    outcome_prices = market.get('outcomePrices', [])
    
    print(f"\nMarket: {question}")
    print(f"Condition ID: {condition_id}")
    print(f"Outcome prices: {outcome_prices}")
    
    # Check if it's AMM or CLOB
    enable_order_book = market.get('enableOrderBook', False)
    print(f"Enable Order Book: {enable_order_book}")
    
    if enable_order_book:
        print(f"\nThis market has CLOB enabled")
        clob_token_ids = market.get('clobTokenIds', [])
        print(f"CLOB Token IDs: {clob_token_ids}")
    else:
        print(f"\nThis market uses AMM (Automated Market Maker)")
        
        # AMM trading uses different endpoints
        # Let's check the Polymarket AMM contract
        
        # Get collateral token (USDC)
        collateral_url = "https://gamma-api.polymarket.com/collateral"
        collateral_response = requests.get(collateral_url, timeout=5)
        
        if collateral_response.status_code == 200:
            collateral = collateral_response.json()
            print(f"\nCollateral token: {collateral}")
            
            # USDC contract address on Polygon
            usdc_address = collateral.get('address')
            print(f"USDC address: {usdc_address}")
            
            # Step 2: Check wallet balance
            print(f"\nStep 2: Checking wallet balance...")
            
            # Connect to Polygon
            polygon_rpc = "https://polygon-rpc.com"
            w3 = Web3(Web3.HTTPProvider(polygon_rpc))
            
            if w3.is_connected():
                print(f"Connected to Polygon")
                
                # Check ETH balance
                eth_balance = w3.eth.get_balance(WALLET_ADDRESS)
                eth_balance_ether = w3.from_wei(eth_balance, 'ether')
                print(f"ETH balance: {eth_balance_ether:.6f} MATIC")
                
                # Check USDC balance (need ABI)
                # USDC is ERC-20
                usdc_abi = [
                    {
                        "constant": True,
                        "inputs": [{"name": "_owner", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "balance", "type": "uint256"}],
                        "type": "function"
                    },
                    {
                        "constant": True,
                        "inputs": [],
                        "name": "decimals",
                        "outputs": [{"name": "", "type": "uint8"}],
                        "type": "function"
                    }
                ]
                
                usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)
                
                try:
                    usdc_balance = usdc_contract.functions.balanceOf(WALLET_ADDRESS).call()
                    decimals = usdc_contract.functions.decimals().call()
                    usdc_balance_human = usdc_balance / (10 ** decimals)
                    print(f"USDC balance: ${usdc_balance_human:.2f}")
                    
                    if usdc_balance_human < 0.01:
                        print(f"❌ Not enough USDC for trading")
                    else:
                        print(f"✅ Enough USDC for trading!")
                        
                        # Step 3: Try to get AMM swap quote
                        print(f"\nStep 3: Getting AMM swap quote...")
                        
                        # Polymarket AMM router
                        # This is complex - need to understand the actual AMM contract
                        # Let's check if there's a swap endpoint
                        
                        # Check Polymarket docs for AMM
                        print(f"\nAMM trading requires:")
                        print(f"1. Approve USDC spending")
                        print(f"2. Call swap function on AMM router")
                        print(f"3. Wait for transaction confirmation")
                        
                        # For now, let's just check if we can get a quote
                        quote_url = f"https://gamma-api.polymarket.com/markets/{market_id}/amm/quote"
                        quote_params = {
                            "amount": "0.01",  # $0.01
                            "side": "buy",  # buy YES
                            "outcomeIndex": 0  # YES outcome
                        }
                        
                        quote_response = requests.get(quote_url, params=quote_params, timeout=5)
                        print(f"Quote response: {quote_response.status_code}")
                        
                        if quote_response.status_code == 200:
                            quote = quote_response.json()
                            print(f"Quote: {quote}")
                        else:
                            print(f"No quote endpoint")
                            
                except Exception as e:
                    print(f"Error checking USDC: {e}")
            else:
                print(f"Failed to connect to Polygon")
        else:
            print(f"Failed to get collateral info")
            
else:
    print(f"Market API error: {response.status_code}")

print("\n" + "="*60)
print("TRADING OPTIONS")
print("="*60)
print("1. CLOB Trading (Order Book)")
print("   - Requires: enableOrderBook=true")
print("   - Uses: token_id from clobTokenIds")
print("   - Status: ❌ Not working (404 errors)")
print("\n2. AMM Trading (Swap)")
print("   - Requires: USDC approval + swap contract")
print("   - Uses: outcomeIndex + amount")
print("   - Status: ⚠️ Need to implement")
print("\n3. Manual Trading (Website)")
print("   - Requires: Browser automation")
print("   - Uses: Selenium/Playwright")
print("   - Status: ✅ Possible backup")
print("="*60)