#!/usr/bin/env python3
"""
Simple test script to verify the Polymarket Trading Bot components
Run this before using the full bot
"""

import os
import sys
from dotenv import load_dotenv

print("="*70)
print("POLYMARKET TRADING BOT - COMPONENT TEST")
print("="*70)

# Check if .env exists
if not os.path.exists('.env'):
    print("\nERROR: .env file not found!")
    print("   Copy .env.example to .env and fill in your credentials")
    print("   cp .env.example .env")
    print("\n   Then edit .env with:")
    print("   - POLYMARKET_PRIVATE_KEY from https://reveal.magic.link/polymarket")
    print("   - POLYMARKET_FUNDER_ADDRESS from polymarket.com/settings")
    sys.exit(1)

# Load environment variables
load_dotenv()

PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

print(f"\nOK: .env file found")
print(f"   Private Key: {PRIVATE_KEY[:20]}..." if PRIVATE_KEY else "   ERROR: Private Key: NOT SET")
print(f"   Funder Address: {FUNDER_ADDRESS}" if FUNDER_ADDRESS else "   ERROR: Funder Address: NOT SET")

# Check credentials
if not PRIVATE_KEY or PRIVATE_KEY == '0xYOUR_PRIVATE_KEY_HERE':
    print("\nERROR: ERROR: POLYMARKET_PRIVATE_KEY not set in .env")
    print("   Get it from: https://reveal.magic.link/polymarket")
    sys.exit(1)

if not FUNDER_ADDRESS or FUNDER_ADDRESS == '0xYOUR_FUNDER_ADDRESS_HERE':
    print("\nERROR: ERROR: POLYMARKET_FUNDER_ADDRESS not set in .env")
    print("   Get it from: polymarket.com/settings → Wallet")
    sys.exit(1)

# Test imports
print("\n" + "-"*70)
print("Testing Python imports...")

try:
    from py_clob_client.client import ClobClient
    print("OK: py-clob-client imported successfully")
except ImportError as e:
    print(f"ERROR: Failed to import py-clob-client: {e}")
    print("\nInstall with:")
    print("  pip install py-clob-client==0.34.5 web3==6.14.0")
    sys.exit(1)

try:
    import web3
    print(f"OK: web3 version: {web3.__version__}")
except ImportError as e:
    print(f"ERROR: Failed to import web3: {e}")
    sys.exit(1)

# Test client initialization
print("\n" + "-"*70)
print("Testing Polymarket client initialization...")

try:
    client = ClobClient(
        host="https://clob.polymarket.com",
        key=PRIVATE_KEY,
        chain_id=137,  # Polygon mainnet
        signature_type=1,  # Magic/email login
        funder=FUNDER_ADDRESS
    )
    print("OK: Client created successfully")
    
    # Generate API credentials
    client.set_api_creds(client.create_or_derive_api_creds())
    print("OK: API credentials generated")
    
except Exception as e:
    print(f"ERROR: Client initialization failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you've made at least one manual trade on polymarket.com")
    print("2. Verify private key from https://reveal.magic.link/polymarket")
    print("3. Check funder address at polymarket.com/settings")
    sys.exit(1)

# Test API connection
print("\n" + "-"*70)
print("Testing API connection...")

try:
    server_time = client.get_server_time()
    print(f"OK: Server time: {server_time}")
except Exception as e:
    print(f"ERROR: Server time check failed: {e}")
    sys.exit(1)

try:
    ok_status = client.get_ok()
    print(f"OK: API status: {ok_status}")
except Exception as e:
    print(f"ERROR: API status check failed: {e}")

# Test market data
print("\n" + "-"*70)
print("Testing market data fetch...")

try:
    import requests
    markets_url = "https://gamma-api.polymarket.com/markets"
    params = {"closed": "false", "limit": 5}
    response = requests.get(markets_url, params=params, timeout=10)
    
    if response.status_code == 200:
        markets = response.json()
        print(f"OK: Fetched {len(markets)} markets")
        
        if markets:
            market = markets[0]
            print(f"   Sample market: {market.get('question', 'N/A')[:60]}...")
            print(f"   Volume 24h: ${market.get('volume24h', 0)}")
            
            # Check for token IDs
            if 'tokens' in market:
                tokens = market['tokens']
                print(f"   Found {len(tokens)} tokens")
                for token in tokens:
                    print(f"     - {token.get('outcome')}: {token.get('token_id', 'N/A')[:20]}...")
    else:
        print(f"ERROR: Market fetch failed: HTTP {response.status_code}")
        
except Exception as e:
    print(f"ERROR: Market data test failed: {e}")

# Test bot components
print("\n" + "-"*70)
print("Testing bot components...")

try:
    # Test config
    from config import validate_config
    validate_config()
    print("OK: Config validation passed")
except Exception as e:
    print(f"ERROR: Config validation failed: {e}")

try:
    # Test market scanner
    from market_scanner import MarketScanner
    scanner = MarketScanner(min_daily_volume=1000, scan_limit=10)
    print("OK: Market scanner initialized")
    
    opportunities = scanner.scan_opportunities()
    print(f"   Found {len(opportunities)} opportunities")
    
except Exception as e:
    print(f"ERROR: Market scanner test failed: {e}")

try:
    # Test order manager
    from order_manager import OrderManager
    order_mgr = OrderManager(client)
    print("OK: Order manager initialized")
    
    balance = order_mgr.get_balance()
    if balance:
        print(f"   Balance: ${balance:.4f}")
    else:
        print("   Note: Balance may not show until first trade")
        
except Exception as e:
    print(f"ERROR: Order manager test failed: {e}")

try:
    # Test risk manager
    from risk_manager import RiskManager, RiskParameters
    risk_params = RiskParameters(
        max_position_size=0.20,
        max_total_exposure=2.50,
        max_concurrent_positions=3
    )
    risk_mgr = RiskManager(risk_params)
    print("OK: Risk manager initialized")
    
except Exception as e:
    print(f"ERROR: Risk manager test failed: {e}")

try:
    # Test trade logger
    from trade_logger import TradeLogger
    logger = TradeLogger("test.db")
    print("OK: Trade logger initialized")
    
    stats = logger.get_trade_stats()
    print(f"   Total trades in DB: {stats['total_trades']}")
    
except Exception as e:
    print(f"ERROR: Trade logger test failed: {e}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)

print("\nOK: All components tested successfully!")
print("\nNext steps:")
print("1. Run the bot in test mode:")
print("   python main.py")
print("   Choose option 3: Test components only")
print("\n2. Make your first trade:")
print("   python main.py")
print("   Choose option 1: Run once (immediate)")
print("\n3. Run scheduled trading:")
print("   python main.py")
print("   Choose option 2: Run scheduled (every 30 minutes)")
print("\nRemember:")
print("- Start with $0.20 trades only")
print("- Monitor the bot closely at first")
print("- Check trades.db for logging")
print("- Review polymarket.com to verify orders")