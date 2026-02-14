#!/usr/bin/env python3
"""
Browser automation to make first trade
"""

import json
import time
from datetime import datetime

print("="*60)
print("BROWSER AUTOMATION TRADE")
print("="*60)

# Step 1: Load trade plan
try:
    with open('first_trade_plan.json', 'r') as f:
        trade_plan = json.load(f)
    
    market_id = trade_plan['market_id']
    question = trade_plan['question']
    amount = trade_plan['amount']
    
    print(f"Trade Plan Loaded:")
    print(f"  Market: {question[:50]}...")
    print(f"  ID: {market_id}")
    print(f"  Amount: {amount}")
    print(f"  Position: {trade_plan['position']}")
    
except Exception as e:
    print(f"Error loading trade plan: {e}")
    # Create default
    market_id = "517310"
    question = "Will Trump deport less than 250,000?"
    amount = "$0.01"

# Step 2: Create browser automation instructions
print(f"\nStep 2: Browser Automation Setup")
print("="*40)

browser_script = f"""
# POLYMARKET TRADE AUTOMATION SCRIPT
# Market: {question}
# Amount: {amount}
# Wallet: 0x9e24439ac551e757e8d578614336b4e482ac9eef

# Steps to automate:
1. Navigate to: https://polymarket.com/market/will-trump-deport-less-than-250000
2. Wait for page load
3. Click "Connect Wallet" button
4. Select "MetaMask" or "WalletConnect"
5. Approve connection
6. Click "Buy YES" button
7. Enter amount: 0.01
8. Click "Place Order"
9. Confirm transaction in wallet
10. Wait for confirmation

# Alternative: Manual execution (faster)
1. Go to: https://polymarket.com
2. Login with Borat14011@gmail.com / Montenegro@
3. Search: "Trump deport less than 250,000"
4. Click market
5. Click "Buy YES"
6. Enter: 0.01
7. Click "Place Order"
8. Confirm
"""

print(browser_script)

# Step 3: Update trade plan with automation status
trade_plan['automation_attempt'] = {
    "timestamp": datetime.now().isoformat(),
    "method": "browser_automation",
    "status": "ready",
    "next_step": "execute_via_browser_or_manual"
}

with open('first_trade_plan.json', 'w') as f:
    json.dump(trade_plan, f, indent=2)

print(f"\nTrade plan updated with automation status")

# Step 4: Check if we can use OpenClaw browser tool
print(f"\nStep 4: OpenClaw Browser Tool")
print("="*40)
print("OpenClaw has a browser tool that can:")
print("1. Open Polymarket website")
print("2. Navigate to market")
print("3. Click buttons")
print("4. Enter amounts")
print("5. Submit trades")
print("\nBut it requires:")
print("1. Chrome extension installed")
print("2. Tab attached to OpenClaw")
print("3. Wallet connected")

# Step 5: Immediate action plan
print(f"\nStep 5: IMMEDIATE ACTION PLAN")
print("="*40)
print("OPTION 1: Manual Trade (Fastest)")
print("  - You do the 8 steps above (2 minutes)")
print("  - Confirm when done")
print("\nOPTION 2: Browser Automation")
print("  - I'll try to automate with OpenClaw")
print("  - Might take 5-10 minutes to set up")
print("\nOPTION 3: Fix API Trading")
print("  - Research correct token_id format")
print("  - Fix CLOB API calls")
print("  - Might take 15-30 minutes")

print(f"\n" + "="*60)
print("RECOMMENDATION: OPTION 1 (Manual)")
print("="*60)
print("Why:")
print("1. Fastest (2 minutes vs 30 minutes)")
print("2. Guaranteed to work (website always works)")
print("3. Gives us real trading data")
print("4. We can then automate based on real flow")
print("\nPlease try manual trade now!")
print("="*60)