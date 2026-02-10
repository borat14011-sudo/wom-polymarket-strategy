"""
Polymarket Trading Bot - Strategy Configuration
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TradingConfig:
    """Configuration for trading strategy"""
    # Market to trade on
    target_market: str = "MicroStrategy 500K BTC Dec 31"
    
    # Trade action: BUY_YES or BUY_NO
    trade_action: str = "BUY_NO"
    
    # Target price in cents (0.01 to 0.99)
    # 83.5¢ = 0.835
    target_price: float = 0.835
    
    # Position size in USD
    position_size: float = 8.00
    
    # Maximum acceptable price deviation
    price_tolerance: float = 0.005  # ±0.5¢
    
    # Minimum balance required to trade
    min_balance: float = 10.00


@dataclass
class BotConfig:
    """Configuration for bot behavior"""
    # Run in headless mode (no browser window)
    headless: bool = True
    
    # Log level: DEBUG, INFO, WARNING, ERROR
    log_level: str = "INFO"
    
    # Maximum retry attempts for operations
    max_retries: int = 3
    
    # Delay between retries in seconds
    retry_delay: int = 5
    
    # Implicit wait timeout in seconds
    implicit_wait: int = 10
    
    # Page load timeout in seconds
    page_load_timeout: int = 30
    
    # Polymarket URLs
    base_url: str = "https://polymarket.com"
    login_url: str = "https://polymarket.com/login"
    markets_url: str = "https://polymarket.com/markets"


def load_config() -> tuple[TradingConfig, BotConfig]:
    """Load configuration from environment variables with defaults"""
    
    trading_config = TradingConfig(
        target_market=os.getenv("TARGET_MARKET", TradingConfig.target_market),
        trade_action=os.getenv("TRADE_ACTION", TradingConfig.trade_action),
        target_price=float(os.getenv("TARGET_PRICE", TradingConfig.target_price)),
        position_size=float(os.getenv("POSITION_SIZE", TradingConfig.position_size)),
    )
    
    bot_config = BotConfig(
        headless=os.getenv("HEADLESS", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", BotConfig.log_level),
        max_retries=int(os.getenv("MAX_RETRIES", BotConfig.max_retries)),
        retry_delay=int(os.getenv("RETRY_DELAY", BotConfig.retry_delay)),
    )
    
    return trading_config, bot_config
