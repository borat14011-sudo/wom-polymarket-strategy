import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import time
from config import *

class PolymarketAPIClient:
    """Enhanced API client with rate limiting, retries, and multiple endpoint support"""
    
    def __init__(self):
        self.session = None
        self.rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS_PER_SECOND)
        self.logger = logging.getLogger(__name__)
        self.active_endpoints = []
        self.failed_endpoints = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            headers={
                'User-Agent': 'PolymarketDataBot/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        await self.test_endpoints()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoints(self):
        """Test all available endpoints and identify working ones"""
        self.logger.info("Testing Polymarket API endpoints...")
        
        endpoints = [POLYMARKET_BASE_URL] + POLYMARKET_BACKUP_URLS
        
        for endpoint in endpoints:
            try:
                async with self.session.get(f"{endpoint}/markets", timeout=10) as response:
                    if response.status == 200:
                        self.active_endpoints.append(endpoint)
                        self.logger.info(f"✓ {endpoint} - ACTIVE")
                    else:
                        self.failed_endpoints.append((endpoint, response.status))
                        self.logger.warning(f"✗ {endpoint} - Status {response.status}")
            except Exception as e:
                self.failed_endpoints.append((endpoint, str(e)))
                self.logger.warning(f"✗ {endpoint} - Error: {str(e)}")
        
        if not self.active_endpoints:
            raise Exception("No working Polymarket API endpoints found!")
            
        self.logger.info(f"Found {len(self.active_endpoints)} working endpoints")
    
    async def get_markets(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Fetch markets from working endpoints"""
        for endpoint in self.active_endpoints:
            try:
                await self.rate_limiter.acquire()
                
                params = {
                    'limit': limit,
                    'offset': offset,
                    'active': 'true',
                    'closed': 'false'
                }
                
                async with self.session.get(f"{endpoint}/markets", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', []) if isinstance(data, dict) else data
                    else:
                        self.logger.warning(f"Failed to fetch markets from {endpoint}: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"Error fetching markets from {endpoint}: {str(e)}")
                continue
        
        return []
    
    async def get_market_details(self, market_id: str) -> Optional[Dict]:
        """Get detailed information for a specific market"""
        for endpoint in self.active_endpoints:
            try:
                await self.rate_limiter.acquire()
                
                async with self.session.get(f"{endpoint}/markets/{market_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.warning(f"Failed to fetch market {market_id} from {endpoint}: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"Error fetching market {market_id} from {endpoint}: {str(e)}")
                continue
        
        return None
    
    async def get_prices(self, market_id: str) -> Optional[Dict]:
        """Get current prices for a market"""
        for endpoint in self.active_endpoints:
            try:
                await self.rate_limiter.acquire()
                
                async with self.session.get(f"{endpoint}/markets/{market_id}/prices") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.warning(f"Failed to fetch prices for {market_id} from {endpoint}: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"Error fetching prices for {market_id} from {endpoint}: {str(e)}")
                continue
        
        return None
    
    async def get_orderbook(self, market_id: str) -> Optional[Dict]:
        """Get orderbook data for a market"""
        for endpoint in self.active_endpoints:
            try:
                await self.rate_limiter.acquire()
                
                async with self.session.get(f"{endpoint}/orderbook/{market_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.warning(f"Failed to fetch orderbook for {market_id} from {endpoint}: {response.status}")
                        
            except Exception as e:
                self.logger.error(f"Error fetching orderbook for {market_id} from {endpoint}: {str(e)}")
                continue
        
        return None

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests_per_second: float):
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request"""
        async with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_request_time = time.time()