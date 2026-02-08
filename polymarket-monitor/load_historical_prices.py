"""
Load historical prices and validate signals on REAL data
"""
import json
import os
from datetime import datetime

def load_price_checkpoints():
    """Load all price checkpoint files"""
    data_dir = "historical-data-scraper/data"
    
    print("[START] Loading historical price data...")
    
    # Find all checkpoint files
    checkpoints = []
    for f in os.listdir(data_dir):
        if f.startswith('prices_checkpoint_') and f.endswith('.json'):
            checkpoints.append(f)
    
    checkpoints.sort()
    print(f"[INFO] Found {len(checkpoints)} checkpoint files")
    
    # Load each checkpoint
    all_prices = {}
    
    for i, checkpoint in enumerate(checkpoints, 1):
        filepath = os.path.join(data_dir, checkpoint)
        size_mb = os.path.getsize(filepath) / 1024 / 1024
        
        print(f"[LOAD] {i}/{len(checkpoints)}: {checkpoint} ({size_mb:.0f} MB)")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                # Merge into all_prices
                if isinstance(data, dict):
                    for market_id, price_data in data.items():
                        if market_id not in all_prices:
                            all_prices[market_id] = []
                        all_prices[market_id].extend(price_data if isinstance(price_data, list) else [price_data])
        
        except Exception as e:
            print(f"[WARN] Failed to load {checkpoint}: {e}")
    
    print(f"\n[COMPLETE] Loaded prices for {len(all_prices)} markets")
    return all_prices

def check_btc_signals(all_prices):
    """Check the 6 BTC signals against historical prices"""
    
    # The 6 signals we found
    signals = [
        ("Will Bitcoin reach $200,000 by December 31, 2026?", "$200K"),
        ("Will Bitcoin reach $150,000 by December 31, 2026?", "$150K"),
        ("Will Bitcoin reach $190,000 by December 31, 2026?", "$190K"),
        ("Will Bitcoin reach $180,000 by December 31, 2026?", "$180K"),
        ("Will Bitcoin reach $160,000 by December 31, 2026?", "$160K"),
        ("Will Bitcoin reach $170,000 by December 31, 2026?", "$170K"),
    ]
    
    print("\n" + "="*80)
    print("[BACKTEST] Validating 6 BTC signals on historical data")
    print("="*80)
    
    # Search for these markets in price data
    for question, label in signals:
        print(f"\n[MARKET] {label}")
        print(f"  Question: {question[:70]}")
        
        # Try to find this market in price data
        # (We need to match by question or look up market_id)
        found = False
        
        # For now, just report structure
        if not found:
            print(f"  Status: Not found in price checkpoints")
            print(f"  Note: Need to match market_id to price data")

def analyze_price_structure():
    """Understand the structure of price checkpoint files"""
    data_dir = "historical-data-scraper/data"
    
    print("\n[ANALYZE] Price data structure")
    
    # Load smallest checkpoint to inspect structure
    smallest = "prices_checkpoint_5000.json"
    filepath = os.path.join(data_dir, smallest)
    
    with open(filepath, 'r') as f:
        data = json.load(f)
        
        print(f"  Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"  Keys (markets): {len(data)}")
            
            # Show first market
            first_key = list(data.keys())[0]
            first_value = data[first_key]
            
            print(f"\n  Sample market ID: {first_key}")
            print(f"  Sample data type: {type(first_value)}")
            
            if isinstance(first_value, list) and first_value:
                print(f"  Sample entry: {first_value[0]}")
            else:
                print(f"  Sample value: {first_value}")
        
        elif isinstance(data, list):
            print(f"  List length: {len(data)}")
            if data:
                print(f"  Sample entry: {data[0]}")

def main():
    # First, understand the structure
    analyze_price_structure()
    
    # Then load all prices
    # all_prices = load_price_checkpoints()
    
    # Finally, validate signals
    # check_btc_signals(all_prices)

if __name__ == "__main__":
    main()
