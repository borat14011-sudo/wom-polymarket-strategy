"""
Analyze general strategies across 93,949 markets dataset.
Focus on:
1. Favorites strategy (>80% probability)
2. Hype fade strategy (overreaction arbitrage)
3. Breakout strategy (momentum/trend)
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

def load_snapshot_sample(n_samples=10000):
    """Load sample from large snapshot file."""
    filepath = Path('markets_snapshot_20260207_221914.json')
    print(f"Loading {n_samples} samples from {filepath}...")
    
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= n_samples:
                break
            try:
                obj = json.loads(line.strip())
                data.append(obj)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {i}: {e}")
                continue
    
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} samples")
    print(f"Columns: {list(df.columns)}")
    return df

def analyze_market_categories(df):
    """Categorize markets by type (politics, crypto, sports, etc.)."""
    # Simple keyword-based categorization
    categories = {
        'politics': ['trump', 'biden', 'election', 'senate', 'house', 'president', 'vote'],
        'crypto': ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'fdv', 'market cap', 'token'],
        'sports': ['nba', 'nfl', 'nhl', 'mlb', 'soccer', 'football', 'basketball', 'championship', 'win'],
        'finance': ['revenue', 'tariff', 'gdp', 'inflation', 'fed', 'rate', 'earnings', 'stock'],
        'tech': ['apple', 'google', 'microsoft', 'ai', 'gpt', 'openai', 'tesla', 'spacex'],
        'entertainment': ['oscar', 'movie', 'film', 'award', 'tv', 'netflix', 'stream']
    }
    
    df['category'] = 'other'
    for cat, keywords in categories.items():
        mask = df['question'].str.lower().apply(lambda x: any(kw in x for kw in keywords))
        df.loc[mask, 'category'] = cat
    
    print("Market categories distribution:")
    print(df['category'].value_counts())
    return df

def test_favorites_strategy(df, threshold=0.8):
    """
    Test betting on high probability outcomes (>80%).
    Assumption: Lower price means higher probability? Need to understand price structure.
    In Polymarket, price between 0-1 represents probability.
    """
    print("\n=== Testing Favorites Strategy (>80% probability) ===")
    # Need to understand price format. Likely 'outcomePrices' list.
    # For binary markets: [price_yes, price_no]
    # Probability = price_yes if betting yes, price_no if betting no
    
    if 'outcomePrices' not in df.columns:
        print("No outcomePrices column found")
        return
    
    # Parse outcome prices
    def parse_prices(x):
        if isinstance(x, str):
            return json.loads(x)
        return x
    
    df['prices'] = df['outcomePrices'].apply(parse_prices)
    
    # For binary markets, assume first price is Yes
    df['prob_yes'] = df['prices'].apply(lambda x: float(x[0]) if x and len(x) > 0 else None)
    df['prob_no'] = df['prices'].apply(lambda x: float(x[1]) if x and len(x) > 1 else None)
    
    # Filter markets with valid probabilities
    valid = df.dropna(subset=['prob_yes', 'prob_no'])
    print(f"Valid binary markets: {len(valid)}")
    
    # Strategy: Bet on outcome with probability > threshold
    # For demonstration, assume we bet Yes when prob_yes > threshold
    favorites = valid[valid['prob_yes'] > threshold]
    print(f"Markets with Yes probability > {threshold}: {len(favorites)}")
    
    # Analyze characteristics
    if len(favorites) > 0:
        print(f"Average Yes probability: {favorites['prob_yes'].mean():.3f}")
        print(f"Average No probability: {favorites['prob_no'].mean():.3f}")
        # Need resolution data to compute actual win rate
        print("Note: Need resolution data to compute actual performance")
    
    return favorites

def analyze_price_distribution(df):
    """Analyze price/probability distribution across markets."""
    print("\n=== Price Distribution Analysis ===")
    if 'outcomePrices' in df.columns:
        def parse_first_price(x):
            if isinstance(x, str):
                prices = json.loads(x)
                return float(prices[0]) if prices else None
            elif isinstance(x, list) and len(x) > 0:
                return float(x[0])
            return None
        
        df['first_price'] = df['outcomePrices'].apply(parse_first_price)
        valid = df.dropna(subset=['first_price'])
        print(f"Valid prices: {len(valid)}")
        print(f"Price stats: min={valid['first_price'].min():.3f}, "
              f"max={valid['first_price'].max():.3f}, "
              f"mean={valid['first_price'].mean():.3f}, "
              f"median={valid['first_price'].median():.3f}")
        
        # Histogram
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        hist = pd.cut(valid['first_price'], bins=bins).value_counts().sort_index()
        print("\nPrice distribution:")
        for bin_label, count in hist.items():
            print(f"  {bin_label}: {count}")

def main():
    # Load sample data
    df = load_snapshot_sample(20000)  # Load 20k samples for analysis
    
    # Basic info
    print(f"\nTotal samples: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Show first few rows
    print("\nFirst row:")
    first_row = df.iloc[0]
    for col in ['id', 'question', 'outcomePrices', 'volume', 'liquidity']:
        if col in df.columns:
            print(f"  {col}: {first_row[col]}")
    
    # Categorize markets
    df = analyze_market_categories(df)
    
    # Analyze price distribution
    analyze_price_distribution(df)
    
    # Test favorites strategy
    test_favorites_strategy(df, threshold=0.8)
    
    # Save sample for further analysis
    df.to_csv('market_sample.csv', index=False)
    print(f"\nSample saved to market_sample.csv")
    
    # Next steps
    print("\n=== Next Steps for Strategy Testing ===")
    print("1. Need resolution data to compute actual win rates")
    print("2. Need time-series price data for momentum/trend analysis")
    print("3. Need to identify hype events (extreme price moves)")
    print("4. Need to merge with resolved markets for ground truth")

if __name__ == '__main__':
    main()