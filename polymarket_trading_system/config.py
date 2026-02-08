"""
PATS Configuration
Global settings for the Polymarket Autonomous Trading System
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from decimal import Decimal

@dataclass
class TradingConfig:
    """Core trading parameters"""
    # Capital Management
    INITIAL_BANKROLL: Decimal = Decimal("10000.00")
    MAX_POSITION_SIZE_PCT: Decimal = Decimal("5.00")  # Max 5% per trade
    MAX_DAILY_RISK_PCT: Decimal = Decimal("10.00")  # Max 10% daily risk
    MAX_CORRELATED_EXPOSURE: Decimal = Decimal("15.00")  # Max 15% correlated
    
    # Signal Generation
    EXTREME_PROBABILITY_THRESHOLD_HIGH: Decimal = Decimal("90.00")
    EXTREME_PROBABILITY_THRESHOLD_LOW: Decimal = Decimal("10.00")
    MIN_LIQUIDITY_USD: Decimal = Decimal("10000.00")  # Minimum market liquidity
    MIN_VOLUME_24H: Decimal = Decimal("5000.00")  # Minimum 24h volume
    
    # Scanning Schedule
    SCAN_INTERVAL_MINUTES: int = 15
    MARKET_ANALYSIS_TIMEFRAMES: List[str] = field(default_factory=lambda: ["1h", "4h", "1d", "1w"])
    
    # Musk Strategy
    MUSK_KEYWORDS: List[str] = field(default_factory=lambda: [
        "musk", "elon", "tesla", "spacex", "x.com", "twitter", "dogecoin",
        "doge", "neuralink", "boring company", "cybertruck", "falcon", "starship"
    ])
    MUSK_HYPE_DECAY_HOURS: int = 48  # Hype fade window
    MUSK_SENTIMENT_THRESHOLD: float = 0.75  # High sentiment = fade opportunity
    
    # Validation Thresholds
    MIN_AGENT_CONSENSUS: int = 4  # Minimum 4 of 6 agents must agree
    MIN_CONFIDENCE_SCORE: Decimal = Decimal("70.00")
    
    # Performance Tracking
    ROI_TARGET_MONTHLY: Decimal = Decimal("5.00")  # 5% monthly target
    MAX_DRAWDOWN_PCT: Decimal = Decimal("20.00")  # 20% max drawdown
    SHARPE_RATIO_MIN: Decimal = Decimal("1.50")

@dataclass
class APIConfig:
    """API configuration"""
    POLYMARKET_API_URL: str = "https://api.polymarket.com"
    POLYMARKET_WS_URL: str = "wss://ws.polymarket.com"
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # WebSocket
    WS_RECONNECT_INTERVAL: int = 5
    WS_PING_INTERVAL: int = 30

@dataclass
class AgentConfig:
    """Multi-agent system configuration"""
    AGENTS: List[Dict] = field(default_factory=lambda: [
        {"name": "TechnicalAnalyst", "weight": 1.0, "type": "technical"},
        {"name": "SentimentAnalyzer", "weight": 1.0, "type": "sentiment"},
        {"name": "WhaleTracker", "weight": 1.2, "type": "whale"},  # Higher weight for whale data
        {"name": "BotDetector", "weight": 0.9, "type": "bot"},
        {"name": "NewsValidator", "weight": 1.0, "type": "news"},
        {"name": "RiskManager", "weight": 1.5, "type": "risk"},  # Highest weight for risk
    ])

@dataclass
class DatabaseConfig:
    """Database configuration"""
    DB_PATH: str = "data/pats_database.db"
    TRADES_TABLE: str = "trades"
    SIGNALS_TABLE: str = "signals"
    PERFORMANCE_TABLE: str = "performance"
    MARKET_DATA_TABLE: str = "market_data"
    
    # Retention
    RAW_DATA_RETENTION_DAYS: int = 90
    AGGREGATED_DATA_RETENTION_DAYS: int = 365

# Global instances
TRADING_CONFIG = TradingConfig()
API_CONFIG = APIConfig()
AGENT_CONFIG = AgentConfig()
DB_CONFIG = DatabaseConfig()
