#!/usr/bin/env python3
"""
API Trading Bot for Polymarket
Executes MSTR Dec 31 trade via API
"""

import os
import sys
from dotenv import load_dotenv
from polymarket_api_client import PolymarketAPIClient

# Load API credentials
load_dotenv('.env.api')

API_KEY = os.getenv('POLYMARKET_API_KEY')
API_SECRET = os.getenv('POLYMARKET_API_SECRET')
PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE')


def main():
    """
    Execute MSTR Dec 31 trading strategy
    """
    print("=" * 60)
    print("🚀 Polymarket API Trading Bot")
    print("=" * 60)
    
    # Validate credentials
    if not API_KEY or API_KEY == 'your_api_key_here':
        print("❌ ERROR: API key not configured!")
        print("   Please edit .env.api with your credentials")
        sys.exit(1)
    
    print("✅ Credentials loaded")
    
    # Initialize API client
    print("\n📡 Connecting to Polymarket API...")
    client = PolymarketAPIClient(API_KEY, API_SECRET, PASSPHRASE)
    
    # Check balance
    print("\n💰 Checking balance...")
    try:
        balance = client.get_balance()
        print(f"   Balance: ${balance:.2f} USDC")
        
        if balance < 8.00:
            print(f"❌ Insufficient balance: ${balance:.2f} < $8.00")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Balance check failed: {e}")
        sys.exit(1)
    
    # Get market details
    print("\n📊 Getting MSTR market details...")
    market_id = "microstrategy-500k-btc-dec-31"
    
    try:
        market = client.get_market(market_id)
        print(f"   Market: {market.get('name', 'Unknown')}")
        print(f"   Status: {market.get('status', 'Unknown')}")
    except Exception as e:
        print(f"❌ Market fetch failed: {e}")
        sys.exit(1)
    
    # Get order book
    print("\n📖 Getting order book...")
    try:
        book = client.get_order_book(market_id)
        print(f"   Order book loaded")
        
        # Show current best prices
        bids = book.get('bids', [])
        asks = book.get('asks', [])
        
        if bids:
            print(f"   Best NO price: {bids[0].get('price', 'N/A')}")
        if asks:
            print(f"   Best YES price: {asks[0].get('price', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Order book fetch failed: {e}")
        sys.exit(1)
    
    # Confirm trade
    print("\n" + "=" * 60)
    print("⚠️  TRADE CONFIRMATION")
    print("=" * 60)
    print("   Market: MicroStrategy 500K BTC by Dec 31")
    print("   Action: BUY NO")
    print("   Price: 83.5¢ ($0.835)")
    print("   Size: $8.00")
    print("   Expected Return: $9.55 (if NO wins)")
    print("=" * 60)
    
    # For safety, require manual confirmation
    print("\n🛑 SAFETY STOP")
    print("   To execute this trade, uncomment the code below")
    print("   in api_trading_bot.py and run again")
    print()
    
    # UNCOMMENT THE FOLLOWING TO EXECUTE REAL TRADE:
    #
    # try:
    #     result = client.place_order(
    #         market_id=market_id,
    #         side="NO",
    #         price=0.835,
    #         size=8.00
    #     )
    #     print("\n🎉 TRADE EXECUTED!")
    #     print(f"   Order ID: {result.get('order_id', 'N/A')}")
    #     print(f"   Status: {result.get('status', 'N/A')}")
    # except Exception as e:
    #     print(f"\n❌ Trade failed: {e}")
    #     sys.exit(1)
    
    print("\n✅ Bot completed successfully (dry run)")
    print("   Edit api_trading_bot.py to enable live trading")
    print("=" * 60)


if __name__ == "__main__":
    main()
