"""
Kalshi Trading Bot Configuration

Environment variables or direct configuration for Kalshi API access.
"""

import os
from pathlib import Path

# =============================================================================
# API CONFIGURATION
# =============================================================================

# Kalshi API Base URLs
API_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
DEMO_API_BASE_URL = "https://demo-api.kalshi.co/trade-api/v2"  # Demo environment

# Use demo/paper trading by default (SAFE)
PAPER_TRADING = os.getenv("KALSHI_PAPER_TRADING", "true").lower() == "true"

# API Credentials - Set via environment variables or replace directly
API_KEY_ID = os.getenv("KALSHI_API_KEY_ID", "")
PRIVATE_KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH", "kalshi_private_key.pem")

# =============================================================================
# TRADING PARAMETERS
# =============================================================================

# Buy the Dip Strategy Settings
class DipBuyerConfig:
    # Minimum price drop to trigger buy (as a percentage, e.g., 0.10 = 10%)
    MIN_DIP_PERCENT = float(os.getenv("KALSHI_MIN_DIP_PERCENT", "0.15"))
    
    # Maximum price to buy at (in cents, $0.50 = 50)
    MAX_BUY_PRICE_CENTS = int(os.getenv("KALSHI_MAX_BUY_PRICE", "50"))
    
    # Minimum price to buy at (avoid near-zero positions)
    MIN_BUY_PRICE_CENTS = int(os.getenv("KALSHI_MIN_BUY_PRICE", "5"))
    
    # Default order size (number of contracts)
    DEFAULT_ORDER_SIZE = int(os.getenv("KALSHI_ORDER_SIZE", "10"))
    
    # Maximum position size per market
    MAX_POSITION_SIZE = int(os.getenv("KALSHI_MAX_POSITION", "100"))
    
    # Maximum total capital to deploy (in cents)
    MAX_CAPITAL_CENTS = int(os.getenv("KALSHI_MAX_CAPITAL", "10000"))  # $100 default
    
    # Markets to monitor (leave empty for all)
    WATCH_TICKERS = os.getenv("KALSHI_WATCH_TICKERS", "").split(",") if os.getenv("KALSHI_WATCH_TICKERS") else []
    
    # Market categories to focus on
    CATEGORIES = os.getenv("KALSHI_CATEGORIES", "").split(",") if os.getenv("KALSHI_CATEGORIES") else []

# =============================================================================
# EXECUTION SETTINGS
# =============================================================================

# Polling interval in seconds
POLL_INTERVAL_SECONDS = int(os.getenv("KALSHI_POLL_INTERVAL", "30"))

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 60

# Order settings
DEFAULT_ORDER_TYPE = "limit"  # "limit" or "market"
ORDER_TIMEOUT_SECONDS = 60

# =============================================================================
# LOGGING
# =============================================================================

LOG_LEVEL = os.getenv("KALSHI_LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("KALSHI_LOG_FILE", "kalshi_bot.log")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_private_key() -> str:
    """Load private key from file."""
    key_path = Path(PRIVATE_KEY_PATH)
    if key_path.exists():
        return key_path.read_text()
    return ""

def validate_config() -> tuple[bool, list[str]]:
    """Validate configuration and return (is_valid, errors)."""
    errors = []
    
    if not API_KEY_ID:
        errors.append("KALSHI_API_KEY_ID not set")
    
    if not Path(PRIVATE_KEY_PATH).exists():
        errors.append(f"Private key file not found: {PRIVATE_KEY_PATH}")
    
    if DipBuyerConfig.MIN_DIP_PERCENT <= 0 or DipBuyerConfig.MIN_DIP_PERCENT >= 1:
        errors.append("MIN_DIP_PERCENT should be between 0 and 1")
    
    return len(errors) == 0, errors

def print_config():
    """Print current configuration (safe, no secrets)."""
    print("=" * 50)
    print("KALSHI BOT CONFIGURATION")
    print("=" * 50)
    print(f"Paper Trading: {PAPER_TRADING}")
    print(f"API Key Set: {'Yes' if API_KEY_ID else 'No'}")
    print(f"Private Key Path: {PRIVATE_KEY_PATH}")
    print(f"Poll Interval: {POLL_INTERVAL_SECONDS}s")
    print("-" * 50)
    print("DIP BUYER SETTINGS:")
    print(f"  Min Dip: {DipBuyerConfig.MIN_DIP_PERCENT * 100:.1f}%")
    print(f"  Buy Price Range: {DipBuyerConfig.MIN_BUY_PRICE_CENTS}¢ - {DipBuyerConfig.MAX_BUY_PRICE_CENTS}¢")
    print(f"  Order Size: {DipBuyerConfig.DEFAULT_ORDER_SIZE} contracts")
    print(f"  Max Position: {DipBuyerConfig.MAX_POSITION_SIZE} contracts")
    print(f"  Max Capital: ${DipBuyerConfig.MAX_CAPITAL_CENTS / 100:.2f}")
    print("=" * 50)


if __name__ == "__main__":
    print_config()
    is_valid, errors = validate_config()
    if not is_valid:
        print("\nConfiguration Errors:")
        for err in errors:
            print(f"  ❌ {err}")
    else:
        print("\n✅ Configuration valid!")
