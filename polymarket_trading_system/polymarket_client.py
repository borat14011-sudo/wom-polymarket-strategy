"""
Polymarket API Client
Handles all interactions with Polymarket API
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Optional, Any
from decimal import Decimal
from datetime import datetime
import logging

from config import API_CONFIG

logger = logging.getLogger(__name__)

class PolymarketClient:
    """Polymarket API client with rate limiting"""
    
    def __init__(self):
        self.base_url = API_CONFIG.POLYMARKET_API_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_times: List[datetime] = []
        self._lock = asyncio.Lock()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=API_CONFIG.REQUEST_TIMEOUT_SECONDS)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        async with self._lock:
            now = datetime.utcnow()
            # Remove requests older than 1 minute
            self._request_times = [
                t for t in self._request_times 
                if (now - t).total_seconds() < 60
            ]
            
            # If at limit, wait
            if len(self._request_times) >= API_CONFIG.MAX_REQUESTS_PER_MINUTE:
                sleep_time = 60 - (now - self._request_times[0]).total_seconds()
                if sleep_time > 0:
                    logger.debug(f"Rate limit reached, sleeping {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
            
            self._request_times.append(datetime.utcnow())
    
    async def _get(self, endpoint: str, params: Dict = None) -> Any:
        """Make GET request with rate limiting"""
        await self._rate_limit()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Rate limited by API, backing off")
                    await asyncio.sleep(5)
                    return await self._get(endpoint, params)
                else:
                    logger.error(f"API error: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    async def get_markets(
        self, 
        limit: int = 100, 
        offset: int = 0,
        active_only: bool = True,
        min_liquidity: Decimal = None
    ) -> List[Dict]:
        """Get list of markets"""
        params = {
            "limit": limit,
            "offset": offset,
            "active": "true" if active_only else "false"
        }
        
        data = await self._get("/markets", params)
        if not data:
            return []
        
        markets = data.get("markets", [])
        
        # Filter by liquidity if specified
        if min_liquidity:
            markets = [
                m for m in markets 
                if Decimal(str(m.get("liquidity", 0))) >= min_liquidity
            ]
        
        return markets
    
    async def get_market(self, market_slug: str) -> Optional[Dict]:
        """Get detailed market information"""
        data = await self._get(f"/markets/{market_slug}")
        return data
    
    async def get_market_orderbook(self, market_slug: str) -> Optional[Dict]:
        """Get market orderbook"""
        data = await self._get(f"/markets/{market_slug}/orderbook")
        return data
    
    async def get_market_trades(self, market_slug: str, limit: int = 100) -> List[Dict]:
        """Get recent trades for a market"""
        params = {"limit": limit}
        data = await self._get(f"/markets/{market_slug}/trades", params)
        return data.get("trades", []) if data else []
    
    async def get_all_active_markets(self, min_liquidity: Decimal = None) -> List[Dict]:
        """Get all active markets with pagination"""
        all_markets = []
        offset = 0
        limit = 100
        
        while True:
            markets = await self.get_markets(
                limit=limit, 
                offset=offset,
                active_only=True,
                min_liquidity=min_liquidity
            )
            
            if not markets:
                break
            
            all_markets.extend(markets)
            
            if len(markets) < limit:
                break
            
            offset += limit
            await asyncio.sleep(0.1)  # Small delay between pages
        
        return all_markets
    
    async def get_market_timeseries(
        self, 
        market_slug: str, 
        timeframe: str = "1d"
    ) -> List[Dict]:
        """Get historical price data"""
        params = {"timeframe": timeframe}
        data = await self._get(f"/markets/{market_slug}/prices", params)
        return data.get("prices", []) if data else []
    
    async def get_whale_activity(self, market_slug: str) -> Dict[str, Any]:
        """Analyze whale activity in a market"""
        trades = await self.get_market_trades(market_slug, limit=500)
        
        if not trades:
            return {"whale_score": Decimal("0"), "whale_trades": []}
        
        # Calculate trade size statistics
        sizes = [Decimal(str(t.get("size", 0))) for t in trades]
        avg_size = sum(sizes) / len(sizes) if sizes else Decimal("0")
        
        # Identify whale trades (top 10% by size)
        sorted_sizes = sorted(sizes, reverse=True)
        whale_threshold = sorted_sizes[len(sorted_sizes) // 10] if len(sorted_sizes) >= 10 else avg_size * 3
        
        whale_trades = [
            t for t in trades 
            if Decimal(str(t.get("size", 0))) >= whale_threshold
        ]
        
        # Calculate whale score (0-100)
        whale_volume = sum(Decimal(str(t.get("size", 0))) for t in whale_trades)
        total_volume = sum(sizes)
        whale_score = (whale_volume / total_volume * 100) if total_volume > 0 else Decimal("0")
        
        return {
            "whale_score": min(whale_score, Decimal("100")),
            "whale_trades": whale_trades,
            "whale_threshold": whale_threshold,
            "total_volume": total_volume,
            "whale_count": len(whale_trades)
        }
    
    async def get_bot_activity_indicators(self, market_slug: str) -> Dict[str, Any]:
        """Detect potential bot activity"""
        trades = await self.get_market_trades(market_slug, limit=1000)
        
        if len(trades) < 50:
            return {"bot_score": Decimal("0"), "indicators": {}}
        
        indicators = {
            "rapid_fire_trades": 0,
            "identical_sizes": 0,
            "round_number_pattern": 0,
            "timing_regularity": 0
        }
        
        # Check for rapid-fire trades (same second)
        timestamps = [t.get("timestamp") for t in trades]
        from collections import Counter
        ts_counts = Counter(timestamps)
        rapid_fire = sum(1 for count in ts_counts.values() if count > 5)
        indicators["rapid_fire_trades"] = min(rapid_fire * 10, 100)
        
        # Check for identical trade sizes
        sizes = [str(t.get("size", 0)) for t in trades]
        size_counts = Counter(sizes)
        identical = sum(1 for count in size_counts.values() if count > 10)
        indicators["identical_sizes"] = min(identical * 10, 100)
        
        # Check for round number patterns
        round_numbers = sum(
            1 for t in trades 
            if str(t.get("size", 0)).rstrip('0').endswith('.') or 
               str(t.get("size", 0)).endswith('00')
        )
        indicators["round_number_pattern"] = min(round_numbers / len(trades) * 100, 100)
        
        # Calculate overall bot score
        bot_score = Decimal(str(sum(indicators.values()) / len(indicators)))
        
        return {
            "bot_score": bot_score,
            "indicators": indicators,
            "trades_analyzed": len(trades)
        }

# Singleton instance
_polymarket_client: Optional[PolymarketClient] = None

async def get_client() -> PolymarketClient:
    """Get or create Polymarket client"""
    global _polymarket_client
    if _polymarket_client is None:
        _polymarket_client = PolymarketClient()
    return _polymarket_client
