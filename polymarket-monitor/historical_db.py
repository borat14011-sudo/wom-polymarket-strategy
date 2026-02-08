"""
Historical Price Database
Stores and retrieves historical price snapshots for Polymarket markets

Schema:
    price_history(
        timestamp INTEGER,
        market_id TEXT,
        yes_price REAL,
        no_price REAL,
        volume_24h REAL,
        PRIMARY KEY (timestamp, market_id)
    )
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class HistoricalDB:
    def __init__(self, db_path="polymarket_history.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS price_history (
                        timestamp INTEGER NOT NULL,
                        market_id TEXT NOT NULL,
                        yes_price REAL NOT NULL,
                        no_price REAL NOT NULL,
                        volume_24h REAL NOT NULL,
                        PRIMARY KEY (timestamp, market_id)
                    )
                """)
                
                # Create indexes for faster lookups
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_market_time 
                    ON price_history(market_id, timestamp DESC)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON price_history(timestamp DESC)
                """)
                
                conn.commit()
                logger.info(f"✅ Database initialized: {self.db_path}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise
    
    def store_snapshot(self, market_id, yes_price, no_price, volume_24h, timestamp=None):
        """
        Store a single market price snapshot
        
        Args:
            market_id: Polymarket market ID
            yes_price: Current YES probability (0-1)
            no_price: Current NO probability (0-1)
            volume_24h: 24-hour trading volume
            timestamp: Unix timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = int(datetime.now().timestamp())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO price_history 
                    (timestamp, market_id, yes_price, no_price, volume_24h)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, market_id, yes_price, no_price, volume_24h))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Failed to store snapshot for {market_id}: {e}")
            raise
    
    def store_snapshots_batch(self, snapshots):
        """
        Store multiple market snapshots in one transaction
        
        Args:
            snapshots: List of tuples (market_id, yes_price, no_price, volume_24h, timestamp)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany("""
                    INSERT OR REPLACE INTO price_history 
                    (timestamp, market_id, yes_price, no_price, volume_24h)
                    VALUES (?, ?, ?, ?, ?)
                """, [(s[4], s[0], s[1], s[2], s[3]) for s in snapshots])
                conn.commit()
                logger.info(f"✅ Stored {len(snapshots)} snapshots")
                
        except Exception as e:
            logger.error(f"❌ Failed to store batch: {e}")
            raise
    
    def get_price_24h_ago(self, market_id):
        """
        Get YES price from 24 hours ago
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            float: YES price 24h ago, or None if not found
        """
        target_time = int((datetime.now() - timedelta(hours=24)).timestamp())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Find closest snapshot within ±2 hours of target
                cursor = conn.execute("""
                    SELECT yes_price, timestamp
                    FROM price_history
                    WHERE market_id = ?
                    AND timestamp BETWEEN ? AND ?
                    ORDER BY ABS(timestamp - ?) ASC
                    LIMIT 1
                """, (market_id, target_time - 7200, target_time + 7200, target_time))
                
                row = cursor.fetchone()
                if row:
                    price, ts = row
                    age_hours = (datetime.now().timestamp() - ts) / 3600
                    logger.debug(f"📊 Found 24h price for {market_id}: {price:.3f} ({age_hours:.1f}h ago)")
                    return price
                else:
                    logger.debug(f"⚠️ No 24h historical data for {market_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to get 24h price for {market_id}: {e}")
            return None
    
    def get_volume_24h_ago(self, market_id):
        """
        Get 24h volume from 24 hours ago (for RVR calculation)
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            float: Volume 24h ago, or None if not found
        """
        target_time = int((datetime.now() - timedelta(hours=24)).timestamp())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT volume_24h, timestamp
                    FROM price_history
                    WHERE market_id = ?
                    AND timestamp BETWEEN ? AND ?
                    ORDER BY ABS(timestamp - ?) ASC
                    LIMIT 1
                """, (market_id, target_time - 7200, target_time + 7200, target_time))
                
                row = cursor.fetchone()
                if row:
                    volume, ts = row
                    age_hours = (datetime.now().timestamp() - ts) / 3600
                    logger.debug(f"📊 Found 24h volume for {market_id}: {volume:.0f} ({age_hours:.1f}h ago)")
                    return volume
                else:
                    logger.debug(f"⚠️ No 24h historical volume for {market_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to get 24h volume for {market_id}: {e}")
            return None
    
    def get_historical_data(self, market_id):
        """
        Get both price and volume from 24h ago (convenience method)
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            dict: {'price_24h_ago': float, 'volume_24h_ago': float} or None
        """
        price = self.get_price_24h_ago(market_id)
        volume = self.get_volume_24h_ago(market_id)
        
        if price is None:
            return None
        
        return {
            'price_24h_ago': price,
            'volume_24h_ago': volume if volume is not None else 0
        }
    
    def get_price_history(self, market_id, hours=168):
        """
        Get full price history for a market
        
        Args:
            market_id: Polymarket market ID
            hours: Number of hours to look back (default 7 days)
            
        Returns:
            List of tuples: (timestamp, yes_price, no_price, volume_24h)
        """
        cutoff_time = int((datetime.now() - timedelta(hours=hours)).timestamp())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, yes_price, no_price, volume_24h
                    FROM price_history
                    WHERE market_id = ?
                    AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (market_id, cutoff_time))
                
                return cursor.fetchall()
                
        except Exception as e:
            logger.error(f"❌ Failed to get price history for {market_id}: {e}")
            return []
    
    def get_stats(self):
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(DISTINCT market_id) as num_markets,
                        COUNT(*) as num_snapshots,
                        MIN(timestamp) as oldest_snapshot,
                        MAX(timestamp) as newest_snapshot
                    FROM price_history
                """)
                
                row = cursor.fetchone()
                if row:
                    num_markets, num_snapshots, oldest, newest = row
                    
                    stats = {
                        'num_markets': num_markets,
                        'num_snapshots': num_snapshots,
                        'oldest_snapshot': datetime.fromtimestamp(oldest) if oldest else None,
                        'newest_snapshot': datetime.fromtimestamp(newest) if newest else None,
                        'db_size_mb': self.db_path.stat().st_size / (1024 * 1024)
                    }
                    
                    return stats
                    
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {}
    
    def cleanup_old_data(self, days=30):
        """
        Remove snapshots older than specified days
        
        Args:
            days: Keep last N days of data (default 30)
        """
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM price_history
                    WHERE timestamp < ?
                """, (cutoff_time,))
                
                deleted = cursor.rowcount
                conn.commit()
                logger.info(f"🧹 Cleaned up {deleted} old snapshots (>{days}d)")
                
                # Vacuum to reclaim space
                conn.execute("VACUUM")
                
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {e}")


# Singleton instance
_db_instance = None

def get_db():
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = HistoricalDB()
    return _db_instance


if __name__ == "__main__":
    # Test the database
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing Historical Database...")
    print("=" * 60)
    
    db = HistoricalDB("test_history.db")
    
    # Store test snapshots
    print("\n1. Storing test snapshots...")
    test_market_id = "test_market_123"
    
    # Simulate snapshots over 48 hours
    now = datetime.now()
    for hours_ago in [48, 24, 12, 6, 1]:
        ts = int((now - timedelta(hours=hours_ago)).timestamp())
        price = 0.5 + (hours_ago * 0.01)  # Price trending down
        volume = 10000 + (hours_ago * 1000)  # Volume increasing
        
        db.store_snapshot(test_market_id, price, 1 - price, volume, timestamp=ts)
        print(f"   {hours_ago}h ago: price={price:.3f}, volume={volume:.0f}")
    
    # Test lookups
    print("\n2. Testing 24h lookups...")
    price_24h = db.get_price_24h_ago(test_market_id)
    volume_24h = db.get_volume_24h_ago(test_market_id)
    
    print(f"   Price 24h ago: {price_24h:.3f}" if price_24h else "   ⚠️ No price found")
    print(f"   Volume 24h ago: {volume_24h:.0f}" if volume_24h else "   ⚠️ No volume found")
    
    # Test historical data
    print("\n3. Testing historical data retrieval...")
    hist_data = db.get_historical_data(test_market_id)
    if hist_data:
        print(f"   ✅ Found: price={hist_data['price_24h_ago']:.3f}, volume={hist_data['volume_24h_ago']:.0f}")
    
    # Test full history
    print("\n4. Testing full history...")
    history = db.get_price_history(test_market_id, hours=72)
    print(f"   Found {len(history)} historical snapshots")
    
    # Get stats
    print("\n5. Database statistics...")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Database tests complete!")
