import os
import sys
sys.path.append('POLYMARKET_TRADING_BOT')

from config import load_config

trading_config, bot_config = load_config()

print("=== TRADING CONFIG ===")
print(f"Target Market: {trading_config.target_market}")
print(f"Trade Action: {trading_config.trade_action}")
print(f"Target Price: {trading_config.target_price}")
print(f"Position Size: ${trading_config.position_size:.2f}")
print(f"Price Tolerance: ±{trading_config.price_tolerance * 100:.1f}%")

print("\n=== BOT CONFIG ===")
print(f"Headless: {bot_config.headless}")
print(f"Log Level: {bot_config.log_level}")
print(f"Max Retries: {bot_config.max_retries}")
print(f"Retry Delay: {bot_config.retry_delay}s")

print("\n=== TRADE SUMMARY ===")
print(f"Buy YES at ≤{trading_config.target_price * 100:.1f}%")
print(f"Position: ${trading_config.position_size:.2f}")
print(f"Acceptable range: {(trading_config.target_price - trading_config.price_tolerance) * 100:.1f}% to {(trading_config.target_price + trading_config.price_tolerance) * 100:.1f}%")