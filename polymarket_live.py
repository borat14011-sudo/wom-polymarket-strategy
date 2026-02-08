#!/usr/bin/env python3
"""
Polymarket Live Data - Working Implementation
Handles actual API structure and provides web scraping fallback
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolymarketLiveData:
    """Working implementation for Polymarket data extraction"""
    
    def __init__(self):
        self.session = None
        self.endpoints = {
            'clob': 'https://clob.polymarket.com',
            'gamma': 'https://gamma-api.polymarket.com'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_clob_markets(self, limit: int = 100) -> List[Dict]:
        """
        Get markets from CLOB API
        NOTE: These are historical markets (2022-2023)
        """
        markets = []
        cursor = None
        
        while len(markets) < limit:
            url = f"{self.endpoints['clob']}/markets"
            params = {'limit': min(100, limit - len(markets))}
            if cursor:
                params['cursor'] = cursor
            
            try:
                async with self.session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        batch = data.get('data', [])
                        markets.extend(batch)
                        
                        # Check for next cursor
                        cursor = data.get('next_cursor')
                        if not cursor or not batch:
                            break
                    else:
                        logger.error(f"CLOB API error: {resp.status}")
                        break
            except Exception as e:
                logger.error(f"Error fetching CLOB markets: {e}")
                break
        
        return markets[:limit]
    
    async def get_gamma_markets(self, limit: int = 100) -> List[Dict]:
        """
        Get markets from Gamma API
        More likely to have current data
        """
        markets = []
        offset = 0
        
        while len(markets) < limit:
            url = f"{self.endpoints['gamma']}/markets"
            params = {
                'limit': min(100, limit - len(markets)),
                'offset': offset,
                'active': 'true',
                'closed': 'false'
            }
            
            try:
                async with self.session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Handle both list and dict responses
                        batch = data if isinstance(data, list) else data.get('data', [])
                        
                        if not batch:
                            break
                        
                        markets.extend(batch)
                        offset += len(batch)
                    else:
                        logger.error(f"Gamma API error: {resp.status}")
                        break
            except Exception as e:
                logger.error(f"Error fetching Gamma markets: {e}")
                break
        
        return markets[:limit]
    
    def normalize_market(self, market: Dict, source: str) -> Dict:
        """Normalize market data from different sources"""
        normalized = {
            'id': market.get('condition_id') or market.get('id') or market.get('market_slug'),
            'source': source,
            'title': market.get('question') or market.get('title') or 'Unknown',
            'description': market.get('description', ''),
            'slug': market.get('market_slug') or market.get('slug', ''),
            'active': market.get('active', False),
            'closed': market.get('closed', False),
            'archived': market.get('archived', False),
            'end_date': market.get('end_date_iso') or market.get('endDate'),
            'category': '',
            'volume': 0.0,
            'liquidity': 0.0,
            'outcomes': [],
            'outcome_prices': [],
            'image': market.get('image', ''),
            'icon': market.get('icon', ''),
            'condition_id': market.get('condition_id', ''),
            'question_id': market.get('question_id', ''),
            'tokens': market.get('tokens', [])
        }
        
        # Try to extract volume from tokens
        if 'tokens' in market and market['tokens']:
            for token in market['tokens']:
                if 'price' in token:
                    normalized['outcome_prices'].append(token['price'])
                if 'outcome' in token:
                    normalized['outcomes'].append(token['outcome'])
        
        return normalized
    
    def is_2025_market(self, market: Dict) -> bool:
        """Check if market is related to 2025"""
        title = market.get('title', '').lower()
        description = market.get('description', '').lower()
        end_date = str(market.get('end_date', '')).lower()
        
        combined = f"{title} {description} {end_date}"
        
        # Check for 2025 references
        if '2025' in combined:
            return True
        if 'twenty-five' in combined:
            return True
        
        return False
    
    async def scrape_website(self) -> List[Dict]:
        """
        Scrape markets directly from polymarket.com
        This is the best method for current data
        """
        markets = []
        
        try:
            # Try to fetch the main page
            url = 'https://polymarket.com'
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    
                    # Extract Next.js data
                    import re
                    next_data_match = re.search(
                        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                        html,
                        re.DOTALL
                    )
                    
                    if next_data_match:
                        try:
                            next_data = json.loads(next_data_match.group(1))
                            
                            # Navigate to markets data
                            if 'props' in next_data:
                                page_props = next_data['props'].get('pageProps', {})
                                
                                # Try different locations
                                if 'markets' in page_props:
                                    raw_markets = page_props['markets']
                                    if isinstance(raw_markets, list):
                                        markets = raw_markets
                                    elif isinstance(raw_markets, dict):
                                        markets = list(raw_markets.values())
                                
                                elif 'initialState' in page_props:
                                    state = page_props['initialState']
                                    if 'markets' in state:
                                        state_markets = state['markets']
                                        if isinstance(state_markets, dict):
                                            markets = list(state_markets.values())
                                        elif isinstance(state_markets, list):
                                            markets = state_markets
                                
                                elif 'dehydratedState' in page_props:
                                    dehydrated = page_props['dehydratedState']
                                    if 'queries' in dehydrated:
                                        for query in dehydrated['queries']:
                                            if 'state' in query and 'data' in query['state']:
                                                data = query['state']['data']
                                                if isinstance(data, list):
                                                    markets.extend(data)
                        
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing Next.js data: {e}")
        
        except Exception as e:
            logger.error(f"Error scraping website: {e}")
        
        return markets
    
    async def get_all_current_markets(self) -> Dict[str, List[Dict]]:
        """Get markets from all available sources"""
        results = {
            'clob': [],
            'gamma': [],
            'scraped': [],
            'combined': [],
            'markets_2025': []
        }
        
        logger.info("Fetching markets from all sources...")
        
        # 1. Try CLOB API (historical)
        logger.info("[1/3] Fetching from CLOB API...")
        clob_raw = await self.get_clob_markets(limit=100)
        results['clob'] = [self.normalize_market(m, 'clob') for m in clob_raw]
        logger.info(f"  Found {len(results['clob'])} markets (historical)")
        
        # 2. Try Gamma API
        logger.info("[2/3] Fetching from Gamma API...")
        gamma_raw = await self.get_gamma_markets(limit=100)
        results['gamma'] = [self.normalize_market(m, 'gamma') for m in gamma_raw]
        logger.info(f"  Found {len(results['gamma'])} markets")
        
        # 3. Try website scraping
        logger.info("[3/3] Scraping website...")
        scraped_raw = await self.scrape_website()
        results['scraped'] = [self.normalize_market(m, 'scraped') for m in scraped_raw]
        logger.info(f"  Found {len(results['scraped'])} markets")
        
        # Combine all sources
        seen_ids = set()
        for source in ['gamma', 'scraped', 'clob']:  # Priority order
            for market in results[source]:
                market_id = market['id']
                if market_id and market_id not in seen_ids:
                    seen_ids.add(market_id)
                    results['combined'].append(market)
        
        # Filter for 2025 markets
        results['markets_2025'] = [
            m for m in results['combined']
            if self.is_2025_market(m)
        ]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TOTAL: {len(results['combined'])} unique markets")
        logger.info(f"2025 MARKETS: {len(results['markets_2025'])}")
        logger.info(f"{'='*60}")
        
        return results
    
    def save_markets(self, markets: List[Dict], filename: str):
        """Save markets to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(markets, f, indent=2, default=str)
        logger.info(f"Saved {len(markets)} markets to {filename}")
    
    def print_summary(self, markets: List[Dict], title: str = "Markets"):
        """Print market summary"""
        print(f"\n{'='*60}")
        print(f"[DATA] {title}: {len(markets)} markets")
        print(f"{'='*60}")
        
        if not markets:
            print("No markets found")
            return
        
        # Show top 10 by checking if volume exists
        sorted_markets = sorted(
            markets,
            key=lambda x: x.get('volume', 0),
            reverse=True
        )[:10]
        
        print("\nTop 10 Markets:")
        for i, m in enumerate(sorted_markets, 1):
            title = m.get('title', 'Unknown')[:50]
            print(f"{i:2d}. {title}")
            print(f"    Active: {m.get('active')} | Closed: {m.get('closed')}")
            print()

async def main():
    """Main execution"""
    print("\n" + "="*60)
    print("POLYMARKET LIVE DATA SYSTEM")
    print("="*60)
    
    async with PolymarketLiveData() as client:
        # Get all markets
        results = await client.get_all_current_markets()
        
        # Print summaries
        client.print_summary(results['clob'], "CLOB API (Historical)")
        client.print_summary(results['gamma'], "Gamma API")
        client.print_summary(results['scraped'], "Website Scraped")
        client.print_summary(results['combined'], "All Combined")
        client.print_summary(results['markets_2025'], "2025 Markets")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        client.save_markets(results['clob'], f'clob_markets_{timestamp}.json')
        client.save_markets(results['gamma'], f'gamma_markets_{timestamp}.json')
        client.save_markets(results['scraped'], f'scraped_markets_{timestamp}.json')
        client.save_markets(results['combined'], f'all_markets_{timestamp}.json')
        client.save_markets(results['markets_2025'], f'2025_markets_{timestamp}.json')
        
        print("\n" + "="*60)
        print("[OK] All data saved to JSON files")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())