#!/usr/bin/env python3
"""
How Polymarket Prices Translate to Odds/Probability
Research and Explanation
"""

print("=" * 70)
print("POLYMARKET PRICING MECHANICS")
print("How Cents Translate to Probability")
print("=" * 70)

print("""
FUNDAMENTAL PRINCIPLE
====================

Polymarket prices are expressed in CENTS (¢), where:

  Price in Cents = IMPLIED PROBABILITY

Examples:
  • 11¢ = 11% probability
  • 89¢ = 89% probability
  • 50¢ = 50% probability (coin flip)
  • 99¢ = 99% probability (almost certain)

HOW IT WORKS
============

1. BINARY MARKETS (YES/NO)
   
   Every market has two outcomes: YES and NO
   Their prices ALWAYS sum to approximately $1.00 (100¢)
   
   Example:
   Market: "Will it rain tomorrow?"
   
   YES price: 30¢ (30% chance of rain)
   NO price:  70¢ (70% chance of no rain)
   
   30¢ + 70¢ = 100¢ ✓

2. HOW TRADERS MAKE MONEY
   
   You BUY shares based on what you think will happen:
   
   Scenario A: You think YES will win
   • Buy YES shares at 30¢
   • If YES happens: Each share pays $1.00
   • Your profit: $1.00 - $0.30 = $0.70 per share
   • Return: 70¢ / 30¢ = 233%
   
   Scenario B: You think NO will win
   • Buy NO shares at 70¢
   • If NO happens: Each share pays $1.00
   • Your profit: $1.00 - $0.70 = $0.30 per share
   • Return: 30¢ / 70¢ = 43%

3. THE MATH OF FAIR PRICING
   
   If the market is perfectly efficient:
   
   Price = True Probability of Event
   
   Example:
   • Fair coin flip should price at 50¢
   • If market prices heads at 60¢, it's OVERVALUED
   • If market prices heads at 40¢, it's UNDERVALUED ← BET HERE

REAL-WORLD EXAMPLE
==================

Market: "Will Trump deport 250K-500K people in 2025?"

Current Prices:
  YES: 87¢
  NO:  13¢

Interpretation:
  • Market thinks 87% chance of 250K-500K deportations
  • Market thinks 13% chance of NOT hitting that range
  
If you think deportations will be OUTSIDE 250K-500K:
  • Buy NO at 13¢
  • If correct: Get $1.00 per share
  • Profit: 87¢ per share (669% return)

If you think deportations WILL be 250K-500K:
  • Buy YES at 87¢
  • If correct: Get $1.00 per share
  • Profit: 13¢ per share (15% return)

KEY INSIGHT
===========

Higher price = Higher probability = Lower payout
Lower price = Lower probability = Higher payout

  Cheap shares (low price) = High risk, high reward
  Expensive shares (high price) = Low risk, low reward

THE TRADER'S EDGE
=================

You make money when you DISAGREE with the market:

  Market price: 11¢ (11% chance)
  Your estimate: 35% chance
  
  → Buy at 11¢ (market says 11%, you say 35%)
  → If you're right, price rises toward 35¢
  → You profit from the price difference

COMMON MISTAKES
===============

❌ Mistake 1: Thinking 89¢ NO means 89% chance of NO
   ✓ Correct: YES at 11¢ means 11% chance of YES
              Therefore NO has 89% chance

❌ Mistake 2: Buying expensive side for "safety"
   Buying YES at 89¢ gives only 12% return
   Buying NO at 11¢ gives 800%+ return (if correct)

❌ Mistake 3: Ignoring fees
   2% entry fee + 2% exit fee = 4% total cost
   A 10¢ share actually costs 10.2¢ to buy
   And pays out 98¢ if you win (after exit fee)

SLIPPAGE REALITY
================

Listed price ≠ Execution price

  Market shows: YES at 11¢
  You try to buy: Might pay 11.5¢ (0.5¢ slippage)
  
Why? Order book depth — not enough sellers at 11¢

At extremes (<5¢ or >95¢), slippage is SEVERE:
  Listed: YES at 99¢
  Actual fill: 99.5¢ (0.5¢ slippage)
  Plus fees: Entry at 99.5¢ × 1.02 = 101.5¢
  → You OVERPAY, can't profit even if right!

SUMMARY
=======

Polymarket prices ARE probabilities:
  • 11¢ = 11% implied probability
  • 89¢ = 89% implied probability
  • Always sum to ~$1.00 (100%)

You profit by finding MISPRICINGS:
  • Market says 11% but true chance is 35%
  • Buy cheap (11¢), sell when price corrects (35¢)

The edge is in being RIGHT when the market is WRONG.

""")

print("=" * 70)
print("RESEARCH COMPLETE")
print("=" * 70)
