"""
Polymarket Live Market Data Monitoring System
Main system for Wom's trading operation
Combines web scraping, API polling, and real-time monitoring
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict
import os

from web_scraper import PolymarketWebScraper
from utils import Logger, DataStorage, AlertManager, PerformanceTracker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'polymarket_monitor_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MarketSnapshot:
    """Snapshot of market data at a point in time"""
    timestamp: str
    market_id: str
    title: str
    price: float
    volume: float
    liquidity: float
    spread: float
    best_bid: float
    best_ask: float
    volume_24h: float
    
    def price_change(self, previous: 'MarketSnapshot') -> float:
        """Calculate price change from previous snapshot"""
        if previous and previous.price > 0:
            return (self.price - previous.price) / previous.price
        return 0.0

class MarketMonitor:
    """
    Comprehensive market monitoring system for Polymarket
    Features:
    - Web scraping for current market data
    - Price change alerts
    - Volume spike detection
    - Market filtering and categorization
    - Data persistence
    - Performance tracking
    """
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.logger = logger
        self.storage = DataStorage()
        self.alert_manager = AlertManager()
        self.performance = PerformanceTracker()
        
        # Market tracking
        self.all_markets: Dict[str, Dict] = {}
        self.markets_2025: Dict[str, Dict] = {}
        self.market_history: Dict[str, List[MarketSnapshot]] = defaultdict(list)
        self.watched_markets: Set[str] = set()
        
        # Monitoring state
        self.is_running = False
        self.last_update = None
        self.update_count = 0
        
    async def initialize(self):
        """Initialize the monitoring system"""
        self.logger.info("Initializing Polymarket Monitor...")
        
        # Create data directory
        os.makedirs('market_data', exist_ok=True)
        os.makedirs('market_history', exist_ok=True)
        os.makedirs('alerts', exist_ok=True)
        
        # Load previous state if exists
        await self.load_state()
        
        self.logger.info("✓ Monitor initialized successfully")
    
    async def load_state(self):
        """Load previous monitoring state"""
        try:
            state_file = 'market_data/monitor_state.json'
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.watched_markets = set(state.get('watched_markets', []))
                    self.logger.info(f"Loaded {len(self.watched_markets)} watched markets")
        except Exception as e:
            self.logger.warning(f"Could not load previous state: {str(e)}")
    
    async def save_state(self):
        """Save current monitoring state"""
        try:
            state = {
                'watched_markets': list(self.watched_markets),
                'last_update': datetime.now().isoformat(),
                'total_markets': len(self.all_markets),
                'markets_2025': len(self.markets_2025)
            }
            
            with open('market_data/monitor_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {str(e)}")
    
    async def fetch_current_markets(self) -> Dict[str, Dict]:
        """Fetch current market data using web scraper"""
        self.logger.info("Fetching current market data...")
        
        async with PolymarketWebScraper() as scraper:
            # Scrape all markets
            all_markets = await scraper.scrape_all_markets()
            
            # Convert to dict by ID
            markets_dict = {}
            for market in all_markets:
                market_id = market.get('id') or market.get('conditionId') or market.get('slug')
                if market_id:
                    markets_dict[market_id] = market
            
            self.logger.info(f"✓ Fetched {len(markets_dict)} markets")
            return markets_dict
    
    async def filter_2025_markets(self, markets: Dict[str, Dict]) -> Dict[str, Dict]:
        """Filter markets for 2025 relevance"""
        markets_2025 = {}
        
        for market_id, market in markets.items():
            try:
                title = market.get('title', '')
                description = market.get('description', '')
                combined = f"{title} {description}".lower()
                
                # Check for 2025 references
                is_2025 = False
                
                if '2025' in combined:
                    is_2025 = True
                elif 'twenty-five' in combined:
                    is_2025 = True
                
                # Check dates
                end_date = str(market.get('endDate', ''))
                if '2025' in end_date:
                    is_2025 = True
                
                created_at = str(market.get('createdAt', ''))
                if '2025' in created_at:
                    is_2025 = True
                
                if is_2025:
                    markets_2025[market_id] = market
                    
            except Exception as e:
                self.logger.debug(f"Error filtering market {market_id}: {str(e)}")
                continue
        
        self.logger.info(f"✓ Filtered {len(markets_2025)} 2025 markets")
        return markets_2025
    
    async def update_markets(self):
        """Update market data and check for changes"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"UPDATE #{self.update_count + 1} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"{'='*80}")
        
        try:
            # Fetch current data
            new_markets = await self.fetch_current_markets()
            
            # Filter for 2025 markets
            new_2025 = await self.filter_2025_markets(new_markets)
            
            # Check for changes
            await self.detect_changes(self.markets_2025, new_2025)
            
            # Update stored data
            self.all_markets = new_markets
            self.markets_2025 = new_2025
            
            # Save snapshots
            await self.save_market_snapshots(new_2025)
            
            # Save to file
            await self.save_current_data()
            
            self.last_update = datetime.now()
            self.update_count += 1
            
            # Print summary
            self.print_summary()
            
            # Save state
            await self.save_state()
            
        except Exception as e:
            self.logger.error(f"Error during update: {str(e)}", exc_info=True)
    
    async def detect_changes(self, old_markets: Dict[str, Dict], new_markets: Dict[str, Dict]):
        """Detect and report changes between market snapshots"""
        
        # Check for price changes
        for market_id, new_market in new_markets.items():
            if market_id in old_markets:
                old_market = old_markets[market_id]
                
                # Get prices
                old_price = self._extract_price(old_market)
                new_price = self._extract_price(new_market)
                
                if old_price > 0 and new_price > 0:
                    price_change = abs(new_price - old_price) / old_price
                    
                    if price_change >= 0.05:  # 5% threshold
                        self.logger.warning(
                            f"🚨 PRICE ALERT: {new_market.get('title', 'Unknown')} - "
                            f"Change: {price_change*100:.2f}% "
                            f"(${old_price:.4f} → ${new_price:.4f})"
                        )
                        
                        # Record alert
                        self.alert_manager.add_price_alert(
                            market_id,
                            new_market.get('title', 'Unknown'),
                            old_price,
                            new_price,
                            0.05
                        )
                
                # Check for volume changes
                old_volume = float(old_market.get('volume', 0))
                new_volume = float(new_market.get('volume', 0))
                
                if old_volume > 0:
                    volume_change = abs(new_volume - old_volume) / old_volume
                    
                    if volume_change >= 0.5:  # 50% threshold
                        self.logger.warning(
                            f"📈 VOLUME ALERT: {new_market.get('title', 'Unknown')} - "
                            f"Change: {volume_change*100:.1f}%"
                        )
                        
                        self.alert_manager.add_volume_alert(
                            market_id,
                            new_market.get('title', 'Unknown'),
                            old_volume,
                            new_volume
                        )
        
        # Check for new markets
        new_market_ids = set(new_markets.keys()) - set(old_markets.keys())
        if new_market_ids:
            self.logger.info(f"🆕 NEW MARKETS: {len(new_market_ids)} new 2025 markets detected")
            for market_id in list(new_market_ids)[:5]:  # Show first 5
                market = new_markets[market_id]
                self.logger.info(f"   - {market.get('title', 'Unknown')}")
        
        # Check for closed/removed markets
        removed_ids = set(old_markets.keys()) - set(new_markets.keys())
        if removed_ids:
            self.logger.info(f"🚫 REMOVED MARKETS: {len(removed_ids)} markets no longer available")
    
    def _extract_price(self, market: Dict) -> float:
        """Extract current price from market data"""
        # Try different price fields
        if 'lastTradePrice' in market:
            return float(market['lastTradePrice'])
        elif 'price' in market:
            return float(market['price'])
        elif 'outcomePrices' in market and market['outcomePrices']:
            return float(market['outcomePrices'][0])
        elif 'bestBid' in market and 'bestAsk' in market:
            bid = float(market.get('bestBid', 0))
            ask = float(market.get('bestAsk', 0))
            if bid > 0 and ask > 0:
                return (bid + ask) / 2
        return 0.0
    
    async def save_market_snapshots(self, markets: Dict[str, Dict]):
        """Save market snapshots to history"""
        timestamp = datetime.now()
        
        for market_id, market in markets.items():
            snapshot = MarketSnapshot(
                timestamp=timestamp.isoformat(),
                market_id=market_id,
                title=market.get('title', 'Unknown'),
                price=self._extract_price(market),
                volume=float(market.get('volume', 0)),
                liquidity=float(market.get('liquidity', 0)),
                spread=float(market.get('spread', 0)),
                best_bid=float(market.get('bestBid', 0)),
                best_ask=float(market.get('bestAsk', 0)),
                volume_24h=float(market.get('volume24h', 0))
            )
            
            self.market_history[market_id].append(snapshot)
            
            # Keep only last 100 snapshots per market
            if len(self.market_history[market_id]) > 100:
                self.market_history[market_id] = self.market_history[market_id][-100:]
    
    async def save_current_data(self):
        """Save current market data to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save all markets
        all_markets_file = f'market_data/all_markets_{timestamp}.json'
        with open(all_markets_file, 'w') as f:
            json.dump(list(self.all_markets.values()), f, indent=2, default=str)
        
        # Save 2025 markets
        markets_2025_file = f'market_data/markets_2025_{timestamp}.json'
        with open(markets_2025_file, 'w') as f:
            json.dump(list(self.markets_2025.values()), f, indent=2, default=str)
        
        # Save latest (overwrite)
        with open('market_data/latest_2025_markets.json', 'w') as f:
            json.dump(list(self.markets_2025.values()), f, indent=2, default=str)
        
        self.logger.info(f"✓ Data saved: {markets_2025_file}")
    
    def print_summary(self):
        """Print current market summary"""
        print("\n" + "="*80)
        print(f"📊 POLYMARKET MONITOR - UPDATE #{self.update_count}")
        print("="*80)
        print(f"Total Markets: {len(self.all_markets)}")
        print(f"2025 Markets: {len(self.markets_2025)}")
        print(f"Last Update: {self.last_update.strftime('%Y-%m-%d %H:%M:%S') if self.last_update else 'Never'}")
        
        # Top markets by volume
        if self.markets_2025:
            print("\n🏆 TOP 2025 MARKETS BY VOLUME:")
            sorted_markets = sorted(
                self.markets_2025.values(),
                key=lambda x: float(x.get('volume', 0)),
                reverse=True
            )[:10]
            
            for i, market in enumerate(sorted_markets, 1):
                volume = float(market.get('volume', 0))
                price = self._extract_price(market)
                title = market.get('title', 'Unknown')[:50]
                
                print(f"{i:2d}. ${volume:>10,.0f} | {price*100:5.1f}¢ | {title}")
        
        # Category breakdown
        categories = defaultdict(int)
        for market in self.markets_2025.values():
            cat = market.get('category', 'Unknown')
            categories[cat] += 1
        
        if categories:
            print("\n📁 CATEGORY BREAKDOWN:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {cat}: {count} markets")
        
        print("="*80 + "\n")
    
    async def run_monitoring(self, duration_minutes: int = None):
        """Run continuous monitoring"""
        self.is_running = True
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info("🚀 STARTING POLYMARKET MONITOR")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Check Interval: {self.check_interval} seconds")
        self.logger.info(f"Duration: {'Unlimited' if duration_minutes is None else f'{duration_minutes} minutes'}")
        self.logger.info(f"{'='*80}\n")
        
        try:
            # Initial update
            await self.update_markets()
            
            start_time = datetime.now()
            
            while self.is_running:
                # Check if duration exceeded
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        self.logger.info(f"✓ Monitoring completed ({duration_minutes} minutes)")
                        break
                
                # Wait for next interval
                self.logger.info(f"⏱️  Next update in {self.check_interval} seconds...")
                await asyncio.sleep(self.check_interval)
                
                # Perform update
                await self.update_markets()
                
        except KeyboardInterrupt:
            self.logger.info("\n⚠️ Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {str(e)}", exc_info=True)
        finally:
            self.is_running = False
            await self.save_state()
            self.logger.info("\n✓ Monitor shutdown complete")
    
    def stop(self):
        """Stop the monitoring system"""
        self.is_running = False
        self.logger.info("Stopping monitor...")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket Live Market Monitor')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument('--duration', type=int, help='Duration in minutes (default: unlimited)')
    args = parser.parse_args()
    
    monitor = MarketMonitor(check_interval=args.interval)
    await monitor.initialize()
    await monitor.run_monitoring(duration_minutes=args.duration)

if __name__ == "__main__":
    asyncio.run(main())