"""
Data pipeline for loading and preparing Polymarket historical data.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List

class PolymarketData:
    """Load and preprocess Polymarket datasets."""
    
    def __init__(self, data_dir: str = '.'):
        self.data_dir = Path(data_dir)
        self.resolved_markets = None
        self.active_markets = None
        self.snapshot = None
        
    def load_resolved_markets(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """Load resolved markets JSON."""
        if filepath is None:
            filepath = self.data_dir / 'polymarket_resolved_markets.json'
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Parse final prices
        df['final_prices'] = df['final_prices'].apply(lambda x: [float(p) for p in x.split('|')])
        df['winner_price'] = df.apply(lambda row: row['final_prices'][0] if row['winner'] == 'Yes' else row['final_prices'][1], axis=1)
        df['loser_price'] = df.apply(lambda row: row['final_prices'][1] if row['winner'] == 'Yes' else row['final_prices'][0], axis=1)
        df['event_end_date'] = pd.to_datetime(df['event_end_date'])
        self.resolved_markets = df
        return df
    
    def load_active_markets(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """Load active markets JSON."""
        if filepath is None:
            filepath = self.data_dir / 'active-markets.json'
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        markets = data['markets']
        df = pd.DataFrame(markets)
        # Parse numeric columns
        numeric_cols = ['volume', 'liquidity', 'volume24hr', 'volume1wk', 'volume1mo', 'volume1yr']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        # Parse outcome prices
        if 'outcomePrices' in df.columns:
            df['outcomePrices'] = df['outcomePrices'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        self.active_markets = df
        return df
    
    def load_snapshot(self, filepath: Optional[str] = None, limit: int = None) -> pd.DataFrame:
        """
        Load large snapshot file (may be memory intensive).
        If limit is provided, load only first N records.
        """
        if filepath is None:
            filepath = self.data_dir / 'markets_snapshot_20260207_221914.json'
        # The snapshot is a JSON array; we can load incrementally
        # For now, we'll attempt to load whole file (89MB)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if limit:
                    # Use iterative JSON parser
                    import ijson
                    items = []
                    parser = ijson.items(f, 'item')
                    for i, obj in enumerate(parser):
                        if i >= limit:
                            break
                        items.append(obj)
                    df = pd.DataFrame(items)
                else:
                    data = json.load(f)
                    df = pd.DataFrame(data)
            self.snapshot = df
            return df
        except Exception as e:
            print(f"Error loading snapshot: {e}")
            # Fallback: read as lines
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    lines.append(json.loads(line.strip()))
                df = pd.DataFrame(lines)
            self.snapshot = df
            return df
    
    def merge_price_history(self, market_ids: List[str]) -> pd.DataFrame:
        """
        Placeholder for merging price history from external source.
        In a real implementation, this would fetch from Polymarket API or on-chain data.
        """
        # TODO: Implement actual price history collection
        print("Price history merging not yet implemented.")
        return pd.DataFrame()
    
    def prepare_backtest_data(self, include_resolved: bool = True, 
                              include_active: bool = False) -> pd.DataFrame:
        """
        Prepare a unified dataset for backtesting.
        Returns DataFrame with columns: market_id, timestamp, price, volume, liquidity, resolved_outcome
        """
        # This is a simplified placeholder
        # In reality, we need time-series price data
        data = []
        if include_resolved and self.resolved_markets is not None:
            for _, row in self.resolved_markets.iterrows():
                # Assume we have only final resolution price
                data.append({
                    'market_id': row['market_id'],
                    'timestamp': row['event_end_date'],
                    'price': row['winner_price'],
                    'volume': row['volume_num'],
                    'liquidity': None,
                    'resolved_outcome': row['winner']
                })
        if include_active and self.active_markets is not None:
            for _, row in self.active_markets.iterrows():
                # Use current best bid/ask or last trade price
                price = None
                if 'lastTradePrice' in row and pd.notna(row['lastTradePrice']):
                    price = row['lastTradePrice']
                elif 'outcomePrices' in row and isinstance(row['outcomePrices'], list) and len(row['outcomePrices']) > 0:
                    price = float(row['outcomePrices'][0])  # first outcome price
                data.append({
                    'market_id': row['id'],
                    'timestamp': pd.Timestamp.now(),
                    'price': price,
                    'volume': row.get('volume', 0),
                    'liquidity': row.get('liquidity', 0),
                    'resolved_outcome': None
                })
        return pd.DataFrame(data)