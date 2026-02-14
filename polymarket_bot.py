#!/usr/bin/env python3
"""
Polymarket Trading Bot - CEUP Strategy Implementation
Using CLOB API with EOA wallet authentication
"""

import os
import json
import time
from decimal import Decimal
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.constants import POLYGON
import requests

# Wallet configuration
PRIVATE_KEY = "0xbfdf6157ac8cf55eb23534d404c77b4d3655cb5c07b3c5386c8eea50df9b2455"
WALLET_ADDRESS = "0xb354e25623617a24164639F63D8b731250AC92d8"

# API configuration
CLOB_HOST = "https://clob.polymarket.com"
CHAIN_ID = POLYGON  # 137 for Polygon mainnet

# Risk management
CAPITAL = Decimal('10.00')  # $10 total capital
MAX_POSITION_SIZE = Decimal('0.02')  # 2% per trade = $0.20
TOTAL_EXPOSURE_LIMIT = Decimal('0.25')  # 25% total = $2.50

class PolymarketBot:
    def __init__(self):
        """Initialize the Polymarket trading bot"""
        print("🔧 Initializing Polymarket Trading Bot...")
        
        # Create wallet from private key
        self.account = Account.from_key(PRIVATE_KEY)
        print(f"✅ Wallet loaded: {self.account.address}")
        
        # Initialize CLOB client
        self.client = ClobClient(
            host=CLOB_HOST,
            chain_id=CHAIN_ID,
            key=self.account.key,
            signature_type=0,  # EOA signature
            funder=self.account.address
        )
        print("✅ CLOB client initialized")
        
        # Get API credentials
        self.api_creds = self.client.create_or_derive_api_creds()
        print("✅ API credentials obtained")
        
        # Initialize trading variables
        self.open_positions = []
        self.total_exposure = Decimal('0.00')
        
    def get_balance(self):
        """Get USDC balance"""
        try:
            # Note: Need to implement balance check via API
            # For now, return placeholder
            return Decimal('10.00')  # Assume $10 for testing
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return Decimal('0.00')
    
    def get_active_markets(self):
        """Fetch active markets from Gamma API"""
        try:
            url = "https://gamma-api.polymarket.com/events?closed=false&limit=50"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            markets = []
            for event in data.get('events', []):
                for market in event.get('markets', []):
                    if market.get('active') and market.get('tokens'):
                        markets.append({
                            'id': market['id'],
                            'question': market['question'],
                            'tokens': market['tokens'],
                            'volume': market.get('volume24h', 0)
                        })
            
            print(f"✅ Found {len(markets)} active markets")
            return markets[:10]  # Return top 10 for testing
            
        except Exception as e:
            print(f"❌ Error fetching markets: {e}")
            return []
    
    def calculate_ceup_score(self, market):
        """
        Calculate Complex Event Uncertainty Pricing score
        Higher score = more complex event = better opportunity
        """
        score = 0
        
        # Score based on question complexity
        question = market['question'].lower()
        
        # Multi-outcome events (higher complexity)
        if 'between' in question or 'range' in question:
            score += 3
        if 'at least' in question or 'more than' in question:
            score += 2
        if 'before' in question or 'after' in question:
            score += 2
        
        # Numeric thresholds (higher complexity)
        if any(word in question for word in ['million', 'billion', 'trillion', '%', 'percent']):
            score += 2
        
        # Political/economic events (higher uncertainty)
        if any(word in question for word in ['trump', 'biden', 'tariff', 'deficit', 'gdp', 'inflation']):
            score += 3
        
        # Time-based events (decay factor)
        if any(word in question for word in ['2025', '2026', '2027', 'end of', 'by']):
            score += 1
        
        # Volume adjustment (higher volume = more efficient pricing)
        volume = market.get('volume', 0)
        if volume < 10000:  # Low volume = potential mispricing
            score += 2
        elif volume > 100000:  # High volume = efficient pricing
            score -= 1
        
        return score
    
    def find_best_opportunity(self):
        """Find the best trading opportunity using CEUP strategy"""
        print("🔍 Scanning for CEUP opportunities...")
        
        markets = self.get_active_markets()
        if not markets:
            print("❌ No markets found")
            return None
        
        # Score each market
        scored_markets = []
        for market in markets:
            score = self.calculate_ceup_score(market)
            if score >= 5:  # Minimum threshold
                scored_markets.append({
                    'market': market,
                    'score': score,
                    'recommendation': 'YES' if score > 7 else 'NO'
                })
        
        # Sort by score (highest first)
        scored_markets.sort(key=lambda x: x['score'], reverse=True)
        
        if scored_markets:
            best = scored_markets[0]
            print(f"🎯 Best opportunity: {best['market']['question'][:50]}...")
            print(f"   CEUP Score: {best['score']}/10, Recommendation: {best['recommendation']}")
            return best
        
        print("❌ No suitable opportunities found")
        return None
    
    def place_order(self, market_id, side, price, size):
        """Place an order on Polymarket"""
        try:
            # Convert to appropriate types
            price_decimal = Decimal(str(price))
            size_decimal = Decimal(str(size))
            
            # Create order arguments
            order_args = OrderArgs(
                token_id=str(market_id),
                price=float(price_decimal),
                size=float(size_decimal),
                side="BUY" if side == "BUY" else "SELL",
                order_type=OrderType.LIMIT
            )
            
            print(f"📤 Placing order: {side} {size} @ {price} on market {market_id}")
            
            # Place the order
            order = self.client.create_and_post_order(order_args)
            
            print(f"✅ Order placed successfully: {order}")
            return order
            
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return None
    
    def execute_trade(self, opportunity):
        """Execute a trade based on opportunity analysis"""
        if not opportunity:
            print("❌ No opportunity to execute")
            return False
        
        market = opportunity['market']
        recommendation = opportunity['recommendation']
        
        # Get token IDs for YES/NO
        tokens = market['tokens']
        yes_token = next((t for t in tokens if t['outcome'] == 'Yes'), None)
        no_token = next((t for t in tokens if t['outcome'] == 'No'), None)
        
        if not yes_token or not no_token:
            print("❌ Could not find YES/NO tokens")
            return False
        
        # Determine which token to trade
        if recommendation == 'YES':
            token_id = yes_token['id']
            side = "BUY"
            # Use current price or estimate
            price = 0.15  # Conservative estimate for testing
        else:
            token_id = no_token['id']
            side = "SELL"
            price = 0.85  # Conservative estimate for testing
        
        # Calculate position size (2% of capital)
        position_size = float(MAX_POSITION_SIZE)
        
        # Check total exposure limit
        if self.total_exposure + Decimal(str(position_size)) > TOTAL_EXPOSURE_LIMIT:
            print(f"⚠️  Would exceed exposure limit. Current: ${self.total_exposure}, Limit: ${TOTAL_EXPOSURE_LIMIT}")
            # Reduce position size
            position_size = float(TOTAL_EXPOSURE_LIMIT - self.total_exposure)
            if position_size <= 0:
                print("❌ No capacity for new positions")
                return False
        
        # Place the order
        order = self.place_order(token_id, side, price, position_size)
        
        if order:
            # Update tracking
            self.open_positions.append({
                'order_id': order.get('order_id'),
                'market_id': market['id'],
                'side': side,
                'size': position_size,
                'price': price
            })
            self.total_exposure += Decimal(str(position_size))
            print(f"📊 Updated exposure: ${self.total_exposure}/{TOTAL_EXPOSURE_LIMIT}")
            return True
        
        return False
    
    def run(self):
        """Main bot execution loop"""
        print("\n" + "="*50)
        print("🚀 POLYMARKET TRADING BOT - CEUP STRATEGY")
        print("="*50)
        
        # Check balance
        balance = self.get_balance()
        print(f"💰 Available balance: ${balance}")
        
        if balance < Decimal('1.00'):
            print("❌ Insufficient balance (need at least $1)")
            return
        
        # Find and execute opportunity
        opportunity = self.find_best_opportunity()
        
        if opportunity:
            print("\n🎯 Executing trade...")
            success = self.execute_trade(opportunity)
            
            if success:
                print("\n✅ TRADE EXECUTED SUCCESSFULLY!")
                print(f"   Market: {opportunity['market']['question'][:60]}...")
                print(f"   Recommendation: {opportunity['recommendation']}")
                print(f"   CEUP Score: {opportunity['score']}/10")
            else:
                print("\n❌ Trade execution failed")
        else:
            print("\n⏸️  No suitable opportunities found. Waiting for next scan...")
        
        print("\n" + "="*50)
        print("Bot execution complete")
        print("="*50)

def main():
    """Main entry point"""
    print("🤖 Starting Polymarket Trading Bot...")
    
    try:
        bot = PolymarketBot()
        bot.run()
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()