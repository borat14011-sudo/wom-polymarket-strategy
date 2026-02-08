import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
from tabulate import tabulate
import os

from api_client import PolymarketAPIClient
from market_parser import MarketParser
from utils import Logger, DataStorage, AlertManager, PerformanceTracker
from config import *

class MarketFetcher:
    """Main market data fetching and processing system"""
    
    def __init__(self):
        self.logger = Logger(__name__, LOG_FILE).logger
        self.parser = MarketParser()
        self.storage = DataStorage()
        self.alert_manager = AlertManager()
        self.performance = PerformanceTracker()
        self.previous_data = {}
        
    async def fetch_all_markets(self, max_markets: int = None) -> List[Dict]:
        """Fetch all available markets with pagination"""
        if max_markets is None:
            max_markets = MAX_MARKETS_TO_MONITOR
            
        self.logger.info("Fetching all markets from Polymarket...")
        all_markets = []
        
        async with PolymarketAPIClient() as client:
            offset = 0
            limit = 100
            
            while offset < max_markets:
                try:
                    markets = await client.get_markets(limit=limit, offset=offset)
                    
                    if not markets:
                        break
                    
                    all_markets.extend(markets)
                    self.performance.record_api_call(True)
                    
                    self.logger.info(f"Fetched {len(markets)} markets (total: {len(all_markets)})")
                    
                    if len(markets) < limit:
                        break
                    
                    offset += limit
                    
                    # Small delay to be respectful to the API
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"Error fetching markets at offset {offset}: {str(e)}")
                    self.performance.record_api_call(False)
                    break
        
        self.performance.record_markets_processed(len(all_markets))
        self.logger.info(f"Total markets fetched: {len(all_markets)}")
        return all_markets
    
    async def fetch_2025_markets(self) -> List[Dict]:
        """Fetch and filter markets for 2025"""
        self.logger.info("Fetching 2025 markets...")
        
        # Fetch all markets
        all_markets = await self.fetch_all_markets()
        
        # Filter for 2025 markets
        markets_2025 = self.parser.filter_2025_markets(all_markets)
        
        # Apply volume and liquidity filters
        filtered_markets = self.parser.filter_by_criteria(markets_2025)
        
        # Parse market data
        parsed_markets = []
        for market in filtered_markets:
            try:
                parsed = self.parser.parse_market_data(market)
                if parsed:
                    parsed_markets.append(parsed)
            except Exception as e:
                self.logger.warning(f"Error parsing market {market.get('id', 'unknown')}: {str(e)}")
                continue
        
        # Sort by volume (highest first)
        parsed_markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
        
        self.logger.info(f"Found {len(parsed_markets)} relevant 2025 markets")
        return parsed_markets
    
    async def fetch_market_details(self, market_id: str) -> Optional[Dict]:
        """Fetch detailed information for a specific market"""
        async with PolymarketAPIClient() as client:
            try:
                details = await client.get_market_details(market_id)
                self.performance.record_api_call(True)
                return details
            except Exception as e:
                self.logger.error(f"Error fetching market details for {market_id}: {str(e)}")
                self.performance.record_api_call(False)
                return None
    
    async def fetch_market_prices(self, market_id: str) -> Optional[Dict]:
        """Fetch current prices for a market"""
        async with PolymarketAPIClient() as client:
            try:
                prices = await client.get_prices(market_id)
                self.performance.record_api_call(True)
                return prices
            except Exception as e:
                self.logger.error(f"Error fetching prices for {market_id}: {str(e)}")
                self.performance.record_api_call(False)
                return None
    
    async def update_market_data(self, markets: List[Dict]) -> List[Dict]:
        """Update market data with current prices and check for alerts"""
        updated_markets = []
        
        async with PolymarketAPIClient() as client:
            for market in markets:
                try:
                    market_id = market['id']
                    
                    # Fetch current prices
                    prices = await client.get_prices(market_id)
                    if prices:
                        # Update market data with new prices
                        old_price = market.get('lastTradePrice', 0)
                        new_price = float(prices.get('price', old_price))
                        
                        market['lastTradePrice'] = new_price
                        market['outcomePrices'] = prices.get('outcomePrices', [])
                        market['lastUpdated'] = datetime.now().isoformat()
                        
                        # Check for price alerts
                        if market_id in self.previous_data:
                            prev_price = self.previous_data[market_id].get('lastTradePrice', 0)
                            if prev_price > 0:
                                self.alert_manager.add_price_alert(
                                    market_id, market['title'], prev_price, new_price,
                                    ALERT_THRESHOLD_PRICE_CHANGE
                                )
                        
                        # Update previous data
                        self.previous_data[market_id] = market.copy()
                    
                    updated_markets.append(market)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.logger.warning(f"Error updating market {market.get('id', 'unknown')}: {str(e)}")
                    continue
        
        return updated_markets
    
    def display_markets_summary(self, markets: List[Dict]):
        """Display a summary of markets"""
        if not markets:
            self.logger.info("No markets to display")
            return
        
        # Prepare data for table
        table_data = []
        for i, market in enumerate(markets[:20], 1):  # Show top 20
            try:
                row = [
                    i,
                    market['title'][:50] + "..." if len(market['title']) > 50 else market['title'],
                    self.storage.format_currency(market['volume']),
                    self.storage.format_currency(market['liquidity']),
                    self.storage.format_price(market.get('lastTradePrice', 0)),
                    market['category'][:15] if market['category'] else 'N/A'
                ]
                table_data.append(row)
            except Exception as e:
                self.logger.warning(f"Error formatting market {i}: {str(e)}")
                continue
        
        # Create table
        headers = ['#', 'Title', 'Volume', 'Liquidity', 'Price', 'Category']
        table = tabulate(table_data, headers=headers, tablefmt=TABLE_FORMAT)
        
        print(f"\n{Fore.CYAN}{'='*DISPLAY_WIDTH}")
        print(f"📊 POLYMARKET 2025 MARKETS SUMMARY")
        print(f"{'='*DISPLAY_WIDTH}{Style.RESET_ALL}")
        print(table)
        print(f"\n{Fore.GREEN}Total 2025 markets: {len(markets)}{Style.RESET_ALL}")
        
        # Category breakdown
        categories = {}
        for market in markets:
            cat = market.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n{Fore.YELLOW}Category Breakdown:{Style.RESET_ALL}")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} markets")
    
    def display_market_details(self, market: Dict):
        """Display detailed information for a single market"""
        print(f"\n{Fore.CYAN}{'='*DISPLAY_WIDTH}")
        print(f"📈 MARKET DETAILS: {market['title']}")
        print(f"{'='*DISPLAY_WIDTH}{Style.RESET_ALL}")
        
        print(f"ID: {market['id']}")
        print(f"Category: {market.get('category', 'N/A')}")
        print(f"Volume: {self.storage.format_currency(market['volume'])}")
        print(f"Liquidity: {self.storage.format_currency(market['liquidity'])}")
        print(f"24h Volume: {self.storage.format_currency(market.get('volume24h', 0))}")
        print(f"Current Price: {self.storage.format_price(market.get('lastTradePrice', 0))}")
        print(f"24h Change: {self.storage.format_percentage(market.get('priceChange24h', 0))}")
        
        if market.get('outcomes'):
            print(f"\nOutcomes:")
            for i, outcome in enumerate(market['outcomes']):
                price = market.get('outcomePrices', [])[i] if i < len(market.get('outcomePrices', [])) else 0
                print(f"  {i+1}. {outcome}: {self.storage.format_price(price)}")
        
        if market.get('endDate'):
            print(f"\nEnd Date: {market['endDate']}")
        
        print(f"\nDescription: {market.get('description', 'No description available')}")
    
    async def save_market_data(self, markets: List[Dict], filename: str = None):
        """Save market data to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"polymarket_2025_{timestamp}.json"
        
        filepath = await self.storage.save_market_data(markets, filename)
        if filepath:
            self.logger.info(f"Market data saved to: {filepath}")
        return filepath
    
    def get_performance_metrics(self) -> Dict:
        """Get system performance metrics"""
        return self.performance.get_metrics()
    
    def display_performance_metrics(self):
        """Display performance metrics"""
        metrics = self.get_performance_metrics()
        
        print(f"\n{Fore.CYAN}{'='*DISPLAY_WIDTH}")
        print(f"⚡ SYSTEM PERFORMANCE METRICS")
        print(f"{'='*DISPLAY_WIDTH}{Style.RESET_ALL}")
        
        print(f"Runtime: {metrics['runtime_seconds']:.1f} seconds")
        print(f"API Calls: {metrics['api_calls']} (Success: {metrics['successful_calls']}, Failed: {metrics['failed_calls']})")
        print(f"Success Rate: {metrics['success_rate']:.1f}%")
        print(f"Markets Processed: {metrics['markets_processed']}")
        print(f"Alerts Generated: {metrics['alerts_generated']}")
        print(f"Last Update: {metrics['last_update']}")

# Import at the end
from colorama import Fore, Style
from config import *