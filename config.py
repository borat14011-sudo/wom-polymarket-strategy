import os
from datetime import datetime

# Polymarket API Configuration
POLYMARKET_BASE_URL = "https://gamma-api.polymarket.com"
POLYMARKET_WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws"

# Alternative API endpoints (backup sources)
POLYMARKET_BACKUP_URLS = [
    "https://api.polymarket.com",
    "https://clob.polymarket.com",
    "https://data.polymarket.com"
]

# API Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 60
RATE_LIMIT_REQUESTS_PER_SECOND = 2
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5

# Market Filtering
TARGET_YEAR = 2025
MIN_VOLUME_THRESHOLD = 1000  # Minimum volume in USD
MIN_LIQUIDITY_THRESHOLD = 500  # Minimum liquidity in USD

# Monitoring Configuration
CHECK_INTERVAL_SECONDS = 30  # How often to check for updates
ALERT_THRESHOLD_PRICE_CHANGE = 0.05  # 5% price change triggers alert
MAX_MARKETS_TO_MONITOR = 100  # Limit number of markets to prevent overload

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = f"polymarket_monitor_{datetime.now().strftime('%Y%m%d')}.log"

# Data Storage
DATA_DIR = "market_data"
CACHE_DURATION_MINUTES = 5

# WebSocket Configuration
WS_RECONNECT_INTERVAL = 30
WS_HEARTBEAT_INTERVAL = 30

# Output Configuration
DISPLAY_WIDTH = 120
TABLE_FORMAT = "grid"

# Trading Configuration (for Wom's operation)
WATCHLIST_CATEGORIES = [
    "politics",
    "crypto", 
    "sports",
    "economics",
    "technology"
]

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)