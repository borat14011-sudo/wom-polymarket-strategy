"""
Browser Automation Module for Polymarket
Uses Playwright/Selenium for JavaScript-rendered content extraction
More reliable than simple HTTP requests for modern web apps
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class PolymarketBrowserAutomation:
    """
    Browser automation for extracting Polymarket data
    Handles JavaScript-rendered content that simple HTTP requests can't access
    """
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        
    async def initialize(self):
        """Initialize browser (Playwright)"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # Create context
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            logger.info("✓ Browser initialized successfully")
            return True
            
        except ImportError:
            logger.error("Playwright not installed. Run: pip install playwright")
            logger.error("Then run: playwright install chromium")
            return False
        except Exception as e:
            logger.error(f"Error initializing browser: {str(e)}")
            return False
    
    async def close(self):
        """Close browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("✓ Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    async def fetch_markets_via_browser(self, url: str = "https://polymarket.com") -> List[Dict]:
        """
        Fetch markets using browser automation
        This can access JavaScript-rendered content
        """
        if not self.page:
            success = await self.initialize()
            if not success:
                return []
        
        try:
            logger.info(f"Navigating to {url}...")
            
            # Navigate to page
            await self.page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait for content to load
            await self.page.wait_for_timeout(3000)
            
            # Extract markets from page
            markets = await self._extract_markets_from_page()
            
            logger.info(f"✓ Extracted {len(markets)} markets via browser")
            return markets
            
        except Exception as e:
            logger.error(f"Error fetching markets via browser: {str(e)}")
            return []
    
    async def _extract_markets_from_page(self) -> List[Dict]:
        """Extract market data from the current page"""
        markets = []
        
        try:
            # Method 1: Extract from Next.js data
            next_data = await self._extract_nextjs_data()
            if next_data:
                page_markets = self._parse_nextjs_markets(next_data)
                markets.extend(page_markets)
            
            # Method 2: Extract from DOM elements
            dom_markets = await self._extract_from_dom()
            markets.extend(dom_markets)
            
            # Method 3: Extract from API calls
            api_markets = await self._intercept_api_calls()
            markets.extend(api_markets)
            
        except Exception as e:
            logger.error(f"Error extracting markets from page: {str(e)}")
        
        return markets
    
    async def _extract_nextjs_data(self) -> Optional[Dict]:
        """Extract Next.js data from page"""
        try:
            # Get __NEXT_DATA__ from page
            next_data = await self.page.evaluate('''() => {
                const nextData = document.getElementById('__NEXT_DATA__');
                if (nextData) {
                    return JSON.parse(nextData.textContent);
                }
                return null;
            }''')
            
            return next_data
        except Exception as e:
            logger.debug(f"Could not extract Next.js data: {str(e)}")
            return None
    
    def _parse_nextjs_markets(self, next_data: Dict) -> List[Dict]:
        """Parse markets from Next.js data"""
        markets = []
        
        try:
            if not next_data or 'props' not in next_data:
                return markets
            
            props = next_data['props']
            page_props = props.get('pageProps', {})
            
            # Look for markets in various locations
            if 'markets' in page_props:
                markets_data = page_props['markets']
                if isinstance(markets_data, list):
                    markets.extend(markets_data)
                elif isinstance(markets_data, dict):
                    markets.extend(markets_data.values())
            
            if 'initialState' in page_props:
                state = page_props['initialState']
                if 'markets' in state:
                    state_markets = state['markets']
                    if isinstance(state_markets, dict):
                        markets.extend(state_markets.values())
                    elif isinstance(state_markets, list):
                        markets.extend(state_markets)
            
            if 'dehydratedState' in page_props:
                dehydrated = page_props['dehydratedState']
                if 'queries' in dehydrated:
                    for query in dehydrated['queries']:
                        if 'state' in query and 'data' in query['state']:
                            data = query['state']['data']
                            if isinstance(data, list):
                                markets.extend(data)
                            elif isinstance(data, dict) and 'markets' in data:
                                markets.extend(data['markets'])
            
        except Exception as e:
            logger.error(f"Error parsing Next.js markets: {str(e)}")
        
        return markets
    
    async def _extract_from_dom(self) -> List[Dict]:
        """Extract market data from DOM elements"""
        markets = []
        
        try:
            # Look for market cards
            market_cards = await self.page.query_selector_all('[data-testid="market-card"]')
            
            for card in market_cards:
                try:
                    market = {}
                    
                    # Extract title
                    title_elem = await card.query_selector('h2, h3, [data-testid="market-title"]')
                    if title_elem:
                        market['title'] = await title_elem.inner_text()
                    
                    # Extract price
                    price_elem = await card.query_selector('[data-testid="market-price"], .price, .market-price')
                    if price_elem:
                        price_text = await price_elem.inner_text()
                        # Parse price (e.g., "45¢" → 0.45)
                        import re
                        price_match = re.search(r'(\d+\.?\d*)', price_text)
                        if price_match:
                            market['price'] = float(price_match.group(1)) / 100
                    
                    # Extract volume
                    volume_elem = await card.query_selector('[data-testid="market-volume"], .volume')
                    if volume_elem:
                        volume_text = await volume_elem.inner_text()
                        market['volume'] = self._parse_volume(volume_text)
                    
                    # Extract link/ID
                    link_elem = await card.query_selector('a')
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href:
                            market['slug'] = href.split('/')[-1]
                            market['id'] = market['slug']
                    
                    if market.get('title'):
                        markets.append(market)
                        
                except Exception as e:
                    continue
            
            logger.info(f"Extracted {len(markets)} markets from DOM")
            
        except Exception as e:
            logger.error(f"Error extracting from DOM: {str(e)}")
        
        return markets
    
    async def _intercept_api_calls(self) -> List[Dict]:
        """Intercept and extract data from API calls"""
        markets = []
        
        try:
            # We can use page.on('response') to intercept API calls
            # For now, we'll use a simpler approach - evaluate script to access window data
            
            window_data = await self.page.evaluate('''() => {
                // Check various global data sources
                const sources = [
                    window.__DATA__,
                    window.__PRELOADED_STATE__,
                    window.__INITIAL_STATE__,
                    window.__APOLLO_STATE__,
                    window.__MARKETS__
                ];
                
                for (const source of sources) {
                    if (source) return source;
                }
                return null;
            }''')
            
            if window_data and isinstance(window_data, dict):
                if 'markets' in window_data:
                    markets_data = window_data['markets']
                    if isinstance(markets_data, list):
                        markets.extend(markets_data)
                    elif isinstance(markets_data, dict):
                        markets.extend(markets_data.values())
            
        except Exception as e:
            logger.debug(f"Could not intercept API calls: {str(e)}")
        
        return markets
    
    def _parse_volume(self, volume_text: str) -> float:
        """Parse volume text to number"""
        import re
        
        # Remove $ and commas
        clean = volume_text.replace('$', '').replace(',', '')
        
        # Check for K, M, B suffixes
        multiplier = 1
        if 'K' in clean.upper():
            multiplier = 1000
            clean = clean.upper().replace('K', '')
        elif 'M' in clean.upper():
            multiplier = 1000000
            clean = clean.upper().replace('M', '')
        elif 'B' in clean.upper():
            multiplier = 1000000000
            clean = clean.upper().replace('B', '')
        
        # Extract number
        match = re.search(r'(\d+\.?\d*)', clean)
        if match:
            return float(match.group(1)) * multiplier
        
        return 0.0
    
    async def scroll_and_load_all(self, max_scrolls: int = 10):
        """Scroll page to load all lazy-loaded content"""
        try:
            for i in range(max_scrolls):
                # Scroll down
                await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
                await self.page.wait_for_timeout(1000)
                
                # Check if we've reached the bottom
                is_at_bottom = await self.page.evaluate('''() => {
                    return (window.innerHeight + window.scrollY) >= document.body.offsetHeight;
                }''')
                
                if is_at_bottom:
                    break
                    
        except Exception as e:
            logger.error(f"Error scrolling page: {str(e)}")
    
    async def fetch_category_markets(self, category: str) -> List[Dict]:
        """Fetch markets for a specific category"""
        url = f"https://polymarket.com/category/{category}"
        return await self.fetch_markets_via_browser(url)
    
    async def fetch_market_details(self, slug: str) -> Optional[Dict]:
        """Fetch detailed information for a specific market"""
        if not self.page:
            await self.initialize()
        
        url = f"https://polymarket.com/event/{slug}"
        
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=60000)
            await self.page.wait_for_timeout(3000)
            
            # Extract detailed data
            next_data = await self._extract_nextjs_data()
            
            if next_data and 'props' in next_data:
                page_props = next_data['props'].get('pageProps', {})
                
                # Look for market data
                if 'market' in page_props:
                    return page_props['market']
                elif 'event' in page_props and 'markets' in page_props['event']:
                    markets = page_props['event']['markets']
                    return markets[0] if markets else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching market details: {str(e)}")
            return None

async def test_browser_automation():
    """Test the browser automation"""
    automation = PolymarketBrowserAutomation()
    
    try:
        markets = await automation.fetch_markets_via_browser()
        print(f"\n✓ Successfully fetched {len(markets)} markets via browser")
        
        if markets:
            print("\nSample markets:")
            for i, market in enumerate(markets[:5], 1):
                title = market.get('title', 'Unknown')
                price = market.get('price', 0)
                volume = market.get('volume', 0)
                print(f"{i}. {title}")
                print(f"   Price: {price:.2f}¢ | Volume: ${volume:,.0f}")
        
        return markets
        
    finally:
        await automation.close()

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    asyncio.run(test_browser_automation())