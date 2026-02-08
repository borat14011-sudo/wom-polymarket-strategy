#!/usr/bin/env python3
"""
Polymarket Data Collector - MVP Version
Collects market snapshots every 15 minutes for backtesting

Usage: python polymarket-data-collector.py
Run as cron job: */15 * * * * python /path/to/polymarket-data-collector.py
"""

import requests
import json
import time
from datetime import datetime
import sqlite3
import os

# Configuration
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
DB_PATH = "polymarket_data.db"
MIN_VOLUME_24H = 100000  # Only track markets with >$100K volume

# Categories we care about (high hype potential)
TARGET_CATEGORIES = [
    "Crypto", "Politics", "Sports", "Pop Culture", 
    "Technology", "Business", "New Markets"
]

class PolymarketCollector:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Markets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS markets (
                market_id TEXT PRIMARY KEY,
                slug TEXT,
                question TEXT,
                description TEXT,
                category TEXT,
                token_id_yes TEXT,
                token_id_no TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                resolved INTEGER DEFAULT 0,
                resolution_outcome TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price_yes REAL,
                price_no REAL,
                volume_24h REAL,
                liquidity REAL,
                best_bid_yes REAL,
                best_ask_yes REAL,
                best_bid_no REAL,
                best_ask_no REAL,
                spread REAL,
                FOREIGN KEY (market_id) REFERENCES markets(market_id),
                UNIQUE(market_id, timestamp)
            )
        ''')
        
        # Index for fast queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_snapshots_market_time 
            ON snapshots(market_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Database initialized: {self.db_path}")
    
    def fetch_markets(self):
        """Fetch active markets from Gamma API"""
        try:
            response = requests.get(
                f"{GAMMA_API}/markets",
                params={
                    "active": "true",
                    "closed": "false",
                    "limit": 100
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter by volume and category
            markets = []
            for market in data:
                volume_24h = float(market.get("volume24hr", 0))
                category = market.get("category", "")
                
                if volume_24h >= MIN_VOLUME_24H:
                    # Check if category matches target
                    if category in TARGET_CATEGORIES or volume_24h > 1000000:
                        markets.append(market)
            
            print(f"✓ Fetched {len(markets)} high-volume markets")
            return markets
            
        except Exception as e:
            print(f"✗ Error fetching markets: {e}")
            return []
    
    def fetch_orderbook(self, token_id):
        """Fetch order book for a token"""
        try:
            response = requests.get(
                f"{CLOB_API}/book",
                params={"token_id": token_id},
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def save_market(self, market):
        """Save or update market metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO markets 
            (market_id, slug, question, description, category, 
             token_id_yes, token_id_no, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            market.get("id"),
            market.get("slug"),
            market.get("question"),
            market.get("description", ""),
            market.get("category", ""),
            market.get("tokens", [{}])[0].get("token_id"),  # YES token
            market.get("tokens", [{}])[1].get("token_id") if len(market.get("tokens", [])) > 1 else None,  # NO token
            market.get("start_date_iso"),
            market.get("end_date_iso")
        ))
        
        conn.commit()
        conn.close()
    
    def save_snapshot(self, market_id, snapshot_data):
        """Save price snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO snapshots 
                (market_id, price_yes, price_no, volume_24h, liquidity,
                 best_bid_yes, best_ask_yes, best_bid_no, best_ask_no, spread)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                market_id,
                snapshot_data.get("price_yes"),
                snapshot_data.get("price_no"),
                snapshot_data.get("volume_24h"),
                snapshot_data.get("liquidity"),
                snapshot_data.get("best_bid_yes"),
                snapshot_data.get("best_ask_yes"),
                snapshot_data.get("best_bid_no"),
                snapshot_data.get("best_ask_no"),
                snapshot_data.get("spread")
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            # Duplicate timestamp - skip
            pass
        finally:
            conn.close()
    
    def collect_snapshot(self, market):
        """Collect single market snapshot"""
        market_id = market.get("id")
        
        # Parse prices from market data
        outcome_prices = market.get("outcomePrices", ["0", "0"])
        try:
            price_yes = float(outcome_prices[0]) if len(outcome_prices) > 0 else 0.5
            price_no = float(outcome_prices[1]) if len(outcome_prices) > 1 else 0.5
        except:
            price_yes, price_no = 0.5, 0.5
        
        # Get orderbook for more detailed data
        tokens = market.get("tokens", [])
        best_bid_yes, best_ask_yes = None, None
        best_bid_no, best_ask_no = None, None
        
        if len(tokens) > 0:
            token_id_yes = tokens[0].get("token_id")
            if token_id_yes:
                book = self.fetch_orderbook(token_id_yes)
                if book:
                    # Parse bids/asks
                    bids = book.get("bids", [])
                    asks = book.get("asks", [])
                    best_bid_yes = float(bids[0].get("price")) if bids else None
                    best_ask_yes = float(asks[0].get("price")) if asks else None
        
        # Calculate spread
        if best_bid_yes and best_ask_yes:
            spread = best_ask_yes - best_bid_yes
        else:
            spread = None
        
        snapshot = {
            "price_yes": price_yes,
            "price_no": price_no,
            "volume_24h": float(market.get("volume24hr", 0)),
            "liquidity": float(market.get("liquidity", 0)),
            "best_bid_yes": best_bid_yes,
            "best_ask_yes": best_ask_yes,
            "best_bid_no": best_bid_no,
            "best_ask_no": best_ask_no,
            "spread": spread
        }
        
        return snapshot
    
    def run(self):
        """Main collection loop"""
        print(f"\n{'='*60}")
        print(f"Polymarket Data Collector - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Fetch markets
        markets = self.fetch_markets()
        
        if not markets:
            print("No markets to collect")
            return
        
        # Collect snapshots
        success_count = 0
        for market in markets:
            try:
                market_id = market.get("id")
                question = market.get("question", "")[:60]
                
                # Save market metadata
                self.save_market(market)
                
                # Collect snapshot
                snapshot = self.collect_snapshot(market)
                self.save_snapshot(market_id, snapshot)
                
                success_count += 1
                print(f"✓ {question}... | Price: ${snapshot['price_yes']:.3f} | Vol: ${snapshot['volume_24h']:,.0f}")
                
                # Rate limiting - be nice to API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"✗ Error collecting {market.get('question', 'Unknown')}: {e}")
        
        print(f"\n{'='*60}")
        print(f"✓ Collected {success_count}/{len(markets)} market snapshots")
        print(f"✓ Database: {self.db_path}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    collector = PolymarketCollector()
    collector.run()
