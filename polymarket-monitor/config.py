"""
Configuration file for Polymarket Monitor
Edit these values to customize behavior
"""

# ===== SIGNAL THRESHOLDS =====
# Minimum RVR (Risk-Volume Ratio) to trigger alert
# RVR = current_volume / avg_24h_volume
# Higher = more selective (only extreme volume spikes)
RVR_THRESHOLD = 2.5

# Minimum absolute ROC (Rate of Change) to trigger alert
# ROC = (current_price - price_12h_ago) / price_12h_ago * 100
# Higher = only alert on larger price movements
ROC_THRESHOLD = 8.0  # percent


# ===== TELEGRAM SETTINGS =====
# Your Telegram username (with @)
TELEGRAM_TARGET = "@MoneyManAmex"

# Silent notifications (don't ping user)
TELEGRAM_SILENT = False


# ===== SCRAPING SETTINGS =====
# Number of markets to track
MARKETS_LIMIT = 50

# Scraping interval in minutes
SCRAPE_INTERVAL_MINUTES = 60


# ===== DATA RETENTION =====
# How many days of historical data to keep
DATA_RETENTION_DAYS = 7

# Anti-spam: Don't alert same market within X hours
ALERT_COOLDOWN_HOURS = 6


# ===== DATABASE =====
# Database file path
DB_PATH = "polymarket_data.db"

# Log file path
LOG_FILE = "monitor.log"


# ===== API SETTINGS =====
# Polymarket API endpoints (usually don't need to change)
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Request timeout in seconds
API_TIMEOUT = 30

# User agent for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


# ===== ADVANCED =====
# Minimum historical data points required for signal calculation
MIN_HISTORY_POINTS = 2

# Daily cleanup time (24-hour format)
CLEANUP_TIME = "03:00"

# Enable debug logging
DEBUG_MODE = False
