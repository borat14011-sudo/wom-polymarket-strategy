#!/usr/bin/env python3
"""
Make first trade via browser automation
"""

import json
import time

print("="*60)
print("BROWSER TRADE - FIRST TRADE")
print("="*60)

# Step 1: Get the best opportunity from latest agent run
print(f"\nStep 1: Finding best opportunity...")

try:
    with open('agent_logs/execution_20260212_053432.json', 'r') as f:
        agent_data = json.load(f)
    
    opportunities = agent_data['agent_results']['opportunity_researcher']['top_opportunities']
    
    if opportunities:
        best_opportunity = opportunities[0]
        market_id = best_opportunity['market_id']
        question = best_opportunity['question']
        condition_id = best_opportunity['condition_id']
        
        print(f"Best opportunity found:")
        print(f"  Market ID: {market_id}")
        print(f"  Question: {question}")
        print(f"  Condition ID: {condition_id[:20]}...")
        
        # Step 2: Create trade plan
        print(f"\nStep 2: Creating trade plan...")
        
        trade_plan = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "market_id": market_id,
            "question": question,
            "condition_id": condition_id,
            "position": "BUY YES",
            "amount": "$0.01",  # First trade - tiny amount
            "reason": "First automated trade - testing system",
            "wallet": "0x9e24439ac551e757e8d578614336b4e482ac9eef",
            "balance": "$10.41",
            "risk": "0.1% of capital",
            "status": "pending"
        }
        
        with open('first_trade_plan.json', 'w') as f:
            json.dump(trade_plan, f, indent=2)
        
        print(f"Trade plan saved to: first_trade_plan.json")
        
        # Step 3: Instructions for manual execution
        print(f"\nStep 3: Manual Execution Instructions")
        print("="*40)
        print("Since API trading is complex, let's do this:")
        print("\n1. Go to: https://polymarket.com")
        print("2. Login with: Borat14011@gmail.com / Montenegro@")
        print("3. Search for: 'Trump deport less than 250,000'")
        print("4. Click on the market")
        print("5. Click 'Buy YES'")
        print("6. Enter amount: $0.01")
        print("7. Click 'Place Order'")
        print("8. Confirm transaction in wallet")
        print("\nThis will:")
        print("✅ Test if wallet has funds")
        print("✅ Test if trading works")
        print("✅ Give us real trading data")
        print("✅ Help fix API issues")
        
        # Step 4: Alternative - browser automation
        print(f"\nStep 4: Browser Automation (Alternative)")
        print("="*40)
        print("If manual doesn't work, I can automate:")
        print("1. Open browser to Polymarket")
        print("2. Login automatically")
        print("3. Place trade")
        print("4. Confirm transaction")
        print("\nBut manual first is safer!")
        
    else:
        print(f"No opportunities found")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("ACTION REQUIRED")
print("="*60)
print("Wom, please try the manual trade above.")
print("It's just $0.01 - basically free!")
print("\nOnce you confirm it works, I can:")
print("1. Fix the Trade Executor agent")
print("2. Enable automated trading")
print("3. Scale up to $0.20 trades (2% of capital)")
print("="*60)