"""
Configuration for Polymarket Trading Bot
Loads credentials from .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Authentication (from https://reveal.magic.link/polymarket)
PRIVATE_KEY = os.getenv('POLYMARKET_PRIVATE_KEY')
FUNDER_ADDRESS = os.getenv('POLYMARKET_FUNDER_ADDRESS')

# Trading parameters
INITIAL_CAPITAL = 10.00  # $10 starting capital
MAX_POSITION_SIZE = 0.20  # $0.20 per trade
MAX_TOTAL_EXPOSURE = 2.50  # $2.50 total exposure
MAX_CONCURRENT_POSITIONS = 3  # Max 3 positions at once

# API settings
CLOB_HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon mainnet
SIGNATURE_TYPE = 1  # Magic/email login (POLY_PROXY)

# Market scanning
MIN_DAILY_VOLUME = 1000  # Skip markets with < $1000 daily volume
SCAN_LIMIT = 100  # Number of markets to fetch

# Database
DB_PATH = "trades.db"

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not PRIVATE_KEY:
        errors.append("POLYMARKET_PRIVATE_KEY not set in .env file")
    
    if not FUNDER_ADDRESS:
        errors.append("POLYMARKET_FUNDER_ADDRESS not set in .env file")
    
    if PRIVATE_KEY and not PRIVATE_KEY.startswith('0x'):
        errors.append("POLYMARKET_PRIVATE_KEY should start with '0x'")
    
    if FUNDER_ADDRESS and not FUNDER_ADDRESS.startswith('0x'):
        errors.append("POLYMARKET_FUNDER_ADDRESS should start with '0x'")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True