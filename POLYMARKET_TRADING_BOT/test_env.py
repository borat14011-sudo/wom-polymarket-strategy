from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("Environment variables loaded:")
print(f"TARGET_MARKET: {os.getenv('TARGET_MARKET')}")
print(f"TRADE_ACTION: {os.getenv('TRADE_ACTION')}")
print(f"TARGET_PRICE: {os.getenv('TARGET_PRICE')}")
print(f"POSITION_SIZE: {os.getenv('POSITION_SIZE')}")
print(f"HEADLESS: {os.getenv('HEADLESS')}")

# Now test config loading
from config import load_config
trading_config, bot_config = load_config()

print("\n=== LOADED CONFIG ===")
print(f"Target Market: {trading_config.target_market}")
print(f"Trade Action: {trading_config.trade_action}")
print(f"Target Price: {trading_config.target_price}")
print(f"Position Size: ${trading_config.position_size:.2f}")
print(f"Headless: {bot_config.headless}")