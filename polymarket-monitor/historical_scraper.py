"""
Historical Price Scraper
Scrapes top 100 active markets from Polymarket Gamma API every hour
and stores snapshots in SQLite database for trend analysis

Run this script via cron every hour to build historical price data.
"""

import requests
import logging
import sys
from datetime import datetime
from pathlib import Path
from historical_db import HistoricalDB

# Setup logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "historical_scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class PolymarketScraper:
    def __init__(self):
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.db = HistoricalDB()
    
    def scrape_and_store(self, limit=100):
        """
        Scrape top active markets and store price snapshots
        
        Args:
            limit: Number of markets to scrape (default 100)
            
        Returns:
            int: Number of snapshots stored
        """
        logger.info(f"[SCRAPE] Starting scrape of top {limit} active markets...")
        
        try:
            # Fetch active markets from Gamma API
            response = requests.get(
                f"{self.gamma_api}/markets",
                params={
                    'limit': limit,
                    'active': True,
                    'closed': False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"[ERROR] API request failed: {response.status_code}")
                return 0
            
            markets = response.json()
            logger.info(f"[INFO] Fetched {len(markets)} active markets")
            
            # Prepare batch insert
            snapshots = []
            timestamp = int(datetime.now().timestamp())
            
            for market in markets:
                try:
                    market_id = market.get('id')
                    if not market_id:
                        continue
                    
                    # Extract price data
                    outcome_prices = market.get('outcomePrices', [])
                    if len(outcome_prices) < 1:
                        logger.warning(f"[WARN] No prices for market {market_id}")
                        continue
                    
                    yes_price = float(outcome_prices[0])
                    no_price = 1 - yes_price
                    
                    # Extract volume
                    volume_24h = float(market.get('volume24hr', 0))
                    
                    snapshots.append((
                        market_id,
                        yes_price,
                        no_price,
                        volume_24h,
                        timestamp
                    ))
                    
                except Exception as e:
                    logger.error(f"[ERROR] Failed to parse market: {e}")
                    continue
            
            # Store all snapshots in batch
            if snapshots:
                self.db.store_snapshots_batch(snapshots)
                logger.info(f"[SUCCESS] Stored {len(snapshots)} price snapshots")
            else:
                logger.warning("[WARN] No snapshots to store")
            
            return len(snapshots)
            
        except Exception as e:
            logger.error(f"[ERROR] Scrape failed: {e}")
            return 0
    
    def run_scrape_job(self):
        """
        Main scrape job entry point
        Called by cron every hour
        """
        start_time = datetime.now()
        logger.info("=" * 60)
        logger.info(f"[START] SCRAPE JOB STARTED: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        try:
            # Scrape and store
            num_stored = self.scrape_and_store(limit=100)
            
            # Log database stats
            stats = self.db.get_stats()
            logger.info(f"[STATS] Database Stats:")
            logger.info(f"   Total markets tracked: {stats.get('num_markets', 0)}")
            logger.info(f"   Total snapshots: {stats.get('num_snapshots', 0)}")
            logger.info(f"   Database size: {stats.get('db_size_mb', 0):.2f} MB")
            
            # Cleanup old data (keep last 30 days)
            self.db.cleanup_old_data(days=30)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("=" * 60)
            logger.info(f"[COMPLETE] SCRAPE JOB COMPLETED: {num_stored} snapshots in {duration:.1f}s")
            logger.info("=" * 60)
            
            return num_stored
            
        except Exception as e:
            logger.error(f"[ERROR] Scrape job failed: {e}")
            return 0


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Polymarket Historical Price Scraper")
    parser.add_argument(
        '--limit', 
        type=int, 
        default=100,
        help='Number of markets to scrape (default: 100)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test scrape and print results'
    )
    
    args = parser.parse_args()
    
    scraper = PolymarketScraper()
    
    if args.test:
        print("[TEST] Running test scrape...")
        print("=" * 60)
        num_stored = scraper.scrape_and_store(limit=10)
        print(f"\n[SUCCESS] Test complete: {num_stored} snapshots stored")
        
        # Show some historical data
        db = HistoricalDB()
        stats = db.get_stats()
        print(f"\n[STATS] Database Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        # Run full scrape job
        scraper.run_scrape_job()


if __name__ == "__main__":
    main()
