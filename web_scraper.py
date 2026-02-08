import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Market:
    """Data class for Polymarket market"""
    id: str
    title: str
    description: str
    category: str
    subcategory: str
    volume: float
    liquidity: float
    outcomes: List[str]
    outcome_prices: List[float]
    best_bid: float
    best_ask: float
    spread: float
    end_date: str
    created_at: str
    closed: bool
    resolved: bool
    resolution: str
    image: str
    slug: str
    market_maker_address: str
    condition_id: str
    question_id: str
    rewards: Dict
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'volume': self.volume,
            'liquidity': self.liquidity,
            'outcomes': self.outcomes,
            'outcomePrices': self.outcome_prices,
            'bestBid': self.best_bid,
            'bestAsk': self.best_ask,
            'spread': self.spread,
            'endDate': self.end_date,
            'createdAt': self.created_at,
            'closed': self.closed,
            'resolved': self.resolved,
            'resolution': self.resolution,
            'image': self.image,
            'slug': self.slug,
            'marketMakerAddress': self.market_maker_address,
            'conditionId': self.condition_id,
            'questionId': self.question_id,
            'rewards': self.rewards
        }

class PolymarketWebScraper:
    """
    Web scraper for Polymarket.com
    Extracts live market data from the website since API is limited to historical data
    """
    
    def __init__(self):
        self.logger = logger
        self.base_url = "https://polymarket.com"
        self.markets_data = []
        self.session = None
        
    async def __aenter__(self):
        import aiohttp
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> str:
        """Fetch HTML page content"""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.error(f"Failed to fetch {url}: Status {response.status}")
                    return ""
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return ""
    
    def extract_json_from_html(self, html: str, pattern: str) -> Optional[Dict]:
        """Extract JSON data embedded in HTML"""
        try:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                json_str = match.group(1)
                # Clean up the JSON string
                json_str = json_str.replace('\\n', '\n').replace('\\t', '\t')
                return json.loads(json_str)
        except Exception as e:
            self.logger.debug(f"Error extracting JSON: {str(e)}")
        return None
    
    async def scrape_all_markets(self, max_pages: int = 10) -> List[Dict]:
        """
        Scrape all markets from polymarket.com
        Uses pagination to get all available markets
        """
        self.logger.info("Starting web scraping of Polymarket.com...")
        all_markets = []
        
        # Try multiple endpoints for market discovery
        endpoints = [
            "https://polymarket.com/api/markets",
            "https://polymarket.com/api/markets?active=true",
            "https://polymarket.com/api/markets?limit=100&offset=0",
        ]
        
        for endpoint in endpoints:
            try:
                self.logger.info(f"Trying endpoint: {endpoint}")
                markets = await self._fetch_markets_api(endpoint)
                if markets:
                    all_markets.extend(markets)
                    self.logger.info(f"✓ Found {len(markets)} markets from {endpoint}")
            except Exception as e:
                self.logger.warning(f"✗ Failed to fetch from {endpoint}: {str(e)}")
        
        # If API endpoints don't work, try scraping the main page
        if not all_markets:
            self.logger.info("API endpoints failed, trying page scraping...")
            markets = await self._scrape_markets_from_page()
            all_markets.extend(markets)
        
        # Remove duplicates
        seen_ids = set()
        unique_markets = []
        for market in all_markets:
            if market['id'] not in seen_ids:
                seen_ids.add(market['id'])
                unique_markets.append(market)
        
        self.logger.info(f"Total unique markets scraped: {len(unique_markets)}")
        return unique_markets
    
    async def _fetch_markets_api(self, url: str) -> List[Dict]:
        """Fetch markets from API endpoint"""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, dict) and 'markets' in data:
                        return data['markets']
                return []
        except Exception as e:
            self.logger.error(f"Error fetching markets API: {str(e)}")
            return []
    
    async def _scrape_markets_from_page(self) -> List[Dict]:
        """Scrape markets from the main page HTML"""
        html = await self.fetch_page(self.base_url)
        if not html:
            return []
        
        markets = []
        
        # Look for Next.js data
        next_data_pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
        next_data = self.extract_json_from_html(html, next_data_pattern)
        
        if next_data and 'props' in next_data:
            try:
                page_props = next_data['props'].get('pageProps', {})
                if 'markets' in page_props:
                    markets.extend(page_props['markets'])
                elif 'initialState' in page_props:
                    state = page_props['initialState']
                    if 'markets' in state:
                        markets.extend(state['markets'].values() if isinstance(state['markets'], dict) else state['markets'])
            except Exception as e:
                self.logger.error(f"Error parsing Next.js data: {str(e)}")
        
        # Look for window.__DATA__
        window_data_pattern = r'window\.__DATA__\s*=\s*(\{.*?\});'
        window_data = self.extract_json_from_html(html, window_data_pattern)
        
        if window_data and 'markets' in window_data:
            markets.extend(window_data['markets'])
        
        # Look for market data in script tags
        script_pattern = r'<script[^>]*>.*?window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});.*?</script>'
        preloaded_state = self.extract_json_from_html(html, script_pattern)
        
        if preloaded_state:
            try:
                if 'markets' in preloaded_state:
                    markets_data = preloaded_state['markets']
                    if isinstance(markets_data, dict):
                        markets.extend(markets_data.values())
                    else:
                        markets.extend(markets_data)
            except Exception as e:
                self.logger.error(f"Error parsing preloaded state: {str(e)}")
        
        self.logger.info(f"Scraped {len(markets)} markets from page")
        return markets
    
    async def scrape_market_details(self, slug: str) -> Optional[Dict]:
        """Scrape detailed information for a specific market"""
        url = f"{self.base_url}/event/{slug}"
        html = await self.fetch_page(url)
        
        if not html:
            return None
        
        try:
            # Extract Next.js data
            next_data_pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
            next_data = self.extract_json_from_html(html, next_data_pattern)
            
            if next_data and 'props' in next_data:
                page_props = next_data['props'].get('pageProps', {})
                
                # Look for market data in various locations
                if 'market' in page_props:
                    return page_props['market']
                elif 'event' in page_props and 'markets' in page_props['event']:
                    return page_props['event']['markets'][0] if page_props['event']['markets'] else None
                elif 'data' in page_props:
                    return page_props['data']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error scraping market details for {slug}: {str(e)}")
            return None
    
    def filter_2025_markets(self, markets: List[Dict]) -> List[Dict]:
        """Filter markets for 2025 relevance"""
        filtered = []
        
        for market in markets:
            try:
                title = market.get('title', '')
                description = market.get('description', '')
                combined = f"{title} {description}".lower()
                
                # Check for 2025 references
                if '2025' in combined or 'twenty-five' in combined:
                    filtered.append(market)
                    continue
                
                # Check end date
                end_date = market.get('endDate', '')
                if '2025' in str(end_date):
                    filtered.append(market)
                    continue
                
                # Check if it's a current prediction market
                created_at = market.get('createdAt', '')
                if '2025' in str(created_at):
                    filtered.append(market)
                    continue
                    
            except Exception as e:
                self.logger.debug(f"Error filtering market: {str(e)}")
                continue
        
        self.logger.info(f"Filtered {len(markets)} markets down to {len(filtered)} 2025 markets")
        return filtered
    
    async def get_live_prices(self, market_id: str) -> Optional[Dict]:
        """Get live prices for a market"""
        # Try orderbook endpoint
        orderbook_urls = [
            f"https://polymarket.com/api/orderbook/{market_id}",
            f"https://clob.polymarket.com/orderbook/{market_id}",
        ]
        
        for url in orderbook_urls:
            try:
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
            except Exception:
                continue
        
        return None
    
    async def save_to_json(self, markets: List[Dict], filename: str = None):
        """Save markets to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"polymarket_scraped_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(markets, f, indent=2, default=str)
            self.logger.info(f"Saved {len(markets)} markets to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
            return None

# Direct extraction method using regex patterns for embedded data
class PolymarketDataExtractor:
    """Extract market data from HTML using various patterns"""
    
    @staticmethod
    def extract_market_cards(html: str) -> List[Dict]:
        """Extract market card data from HTML"""
        markets = []
        
        # Pattern for market cards
        card_pattern = r'data-testid="market-card"[^>]*>(.*?)</div>\s*</div>\s*</div>'
        cards = re.findall(card_pattern, html, re.DOTALL)
        
        for card in cards:
            try:
                market = {}
                
                # Extract title
                title_match = re.search(r'<h[23][^>]*>(.*?)</h[23]>', card)
                if title_match:
                    market['title'] = re.sub(r'<[^>]+>', '', title_match.group(1))
                
                # Extract price
                price_match = re.search(r'(\d+\.?\d*)¢', card)
                if price_match:
                    market['price'] = float(price_match.group(1)) / 100
                
                # Extract volume
                volume_match = re.search(r'Vol\.?\s*\$?([\d,]+\.?\d*)[KMB]?', card)
                if volume_match:
                    volume_str = volume_match.group(1).replace(',', '')
                    market['volume'] = float(volume_str)
                
                if market:
                    markets.append(market)
                    
            except Exception as e:
                continue
        
        return markets
    
    @staticmethod
    def extract_graphql_data(html: str) -> List[Dict]:
        """Extract GraphQL data from HTML"""
        markets = []
        
        # Look for GraphQL responses embedded in scripts
        pattern = r'"markets":\s*(\[.*?\])'
        matches = re.findall(pattern, html, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, list):
                    markets.extend(data)
            except:
                continue
        
        return markets