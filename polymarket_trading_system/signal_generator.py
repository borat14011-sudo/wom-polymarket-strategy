"""
Signal Generator Module
Detects extreme probability opportunities and generates trading signals
"""
import asyncio
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging
import re

from config import TRADING_CONFIG
from polymarket_client import PolymarketClient
from database import Signal, db_manager

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Generates trading signals based on multiple strategies"""
    
    def __init__(self):
        self.config = TRADING_CONFIG
        self.extreme_high = self.config.EXTREME_PROBABILITY_THRESHOLD_HIGH
        self.extreme_low = self.config.EXTREME_PROBABILITY_THRESHOLD_LOW
    
    async def scan_for_opportunities(self, client: PolymarketClient) -> List[Signal]:
        """Main scanning function - runs every 15 minutes"""
        logger.info("Starting market scan for opportunities...")
        
        signals = []
        
        # Get all active markets with sufficient liquidity
        markets = await client.get_all_active_markets(
            min_liquidity=self.config.MIN_LIQUIDITY_USD
        )
        
        logger.info(f"Found {len(markets)} markets with sufficient liquidity")
        
        # Filter markets by volume
        qualified_markets = [
            m for m in markets 
            if Decimal(str(m.get("volume24hr", 0))) >= self.config.MIN_VOLUME_24H
        ]
        
        logger.info(f"{len(qualified_markets)} markets pass volume filter")
        
        # Check each market for opportunities
        for market in qualified_markets:
            try:
                signal = await self._analyze_market(client, market)
                if signal:
                    signals.append(signal)
                    logger.info(f"Signal generated: {market.get('slug')} - {signal.strategy}")
            except Exception as e:
                logger.error(f"Error analyzing {market.get('slug')}: {e}")
                continue
        
        logger.info(f"Scan complete. Generated {len(signals)} signals")
        return signals
    
    async def _analyze_market(self, client: PolymarketClient, market: Dict) -> Optional[Signal]:
        """Analyze a single market for trading opportunities"""
        market_slug = market.get("slug")
        market_id = market.get("id")
        question = market.get("question", "")
        
        # Get current probability
        probability = Decimal(str(market.get("probabilityYes", 0))) * 100
        
        # Get orderbook for spread calculation
        orderbook = await client.get_market_orderbook(market_slug)
        
        # Calculate spread
        spread = self._calculate_spread(orderbook)
        if spread > Decimal("5.00"):  # Skip if spread > 5%
            return None
        
        # Check for extreme probability opportunity
        extreme_signal = self._check_extreme_probability(market, probability)
        if extreme_signal:
            return extreme_signal
        
        # Check for Musk Hype Fade opportunity
        musk_signal = await self._check_musk_opportunity(client, market, probability)
        if musk_signal:
            return musk_signal
        
        return None
    
    def _calculate_spread(self, orderbook: Optional[Dict]) -> Decimal:
        """Calculate bid-ask spread"""
        if not orderbook:
            return Decimal("100")
        
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])
        
        if not bids or not asks:
            return Decimal("100")
        
        best_bid = Decimal(str(bids[0].get("price", 0))) * 100
        best_ask = Decimal(str(asks[0].get("price", 0))) * 100
        
        return best_ask - best_bid
    
    def _check_extreme_probability(self, market: Dict, probability: Decimal) -> Optional[Signal]:
        """Check for extreme probability reversal opportunity"""
        # Extreme high - fade the crowd (bet on NO)
        if probability >= self.extreme_high:
            return self._create_signal(
                market=market,
                probability=probability,
                side="no",
                strategy="extreme_high_fade",
                confidence=self._calculate_extreme_confidence(probability, "high"),
                reasoning=f"Probability at {probability}% - extreme high, fade opportunity"
            )
        
        # Extreme low - value opportunity (bet on YES)
        if probability <= self.extreme_low:
            return self._create_signal(
                market=market,
                probability=probability,
                side="yes",
                strategy="extreme_low_value",
                confidence=self._calculate_extreme_confidence(probability, "low"),
                reasoning=f"Probability at {probability}% - extreme low, value opportunity"
            )
        
        return None
    
    async def _check_musk_opportunity(
        self, 
        client: PolymarketClient, 
        market: Dict, 
        probability: Decimal
    ) -> Optional[Signal]:
        """Check for Musk Hype Fade opportunity"""
        question = market.get("question", "").lower()
        description = market.get("description", "").lower()
        
        # Check if market is Musk-related
        is_musk_market = any(
            keyword in question or keyword in description 
            for keyword in self.config.MUSK_KEYWORDS
        )
        
        if not is_musk_market:
            return None
        
        # Get historical data
        timeseries = await client.get_market_timeseries(market.get("slug"), "1d")
        
        if len(timeseries) < 3:
            return None
        
        # Analyze price momentum
        recent_prices = [Decimal(str(p.get("probability", 0))) * 100 for p in timeseries[-7:]]
        
        if len(recent_prices) < 3:
            return None
        
        # Calculate momentum
        price_change_24h = recent_prices[-1] - recent_prices[-2] if len(recent_prices) >= 2 else Decimal("0")
        price_change_7d = recent_prices[-1] - recent_prices[0] if len(recent_prices) >= 7 else Decimal("0")
        
        # Musk Hype Fade conditions:
        # 1. Probability has spiked recently (>15% in 24h)
        # 2. Probability is high (>60%)
        # 3. High sentiment/social buzz (implied by volume spike)
        
        volume_24h = Decimal(str(market.get("volume24hr", 0)))
        avg_volume = Decimal(str(market.get("volume", 0))) / 30  # Approximate daily average
        
        volume_spike = volume_24h > avg_volume * 3 if avg_volume > 0 else False
        
        if price_change_24h > Decimal("15") and probability > Decimal("60") and volume_spike:
            # Hype spike detected - fade it
            return self._create_signal(
                market=market,
                probability=probability,
                side="no",
                strategy="musk_hype_fade",
                confidence=min(price_change_24h * 2, Decimal("85")),
                reasoning=f"Musk hype spike: +{price_change_24h:.1f}% in 24h on high volume",
                metadata={
                    "price_change_24h": float(price_change_24h),
                    "price_change_7d": float(price_change_7d),
                    "volume_spike": float(volume_24h / avg_volume) if avg_volume > 0 else 0,
                    "is_musk_market": True
                }
            )
        
        return None
    
    def _calculate_extreme_confidence(self, probability: Decimal, extreme_type: str) -> Decimal:
        """Calculate confidence score for extreme probability signals"""
        if extreme_type == "high":
            # Higher probability = higher confidence in fade
            base_confidence = (probability - self.extreme_high) * 2
        else:
            # Lower probability = higher confidence in value
            base_confidence = (self.extreme_low - probability) * 2
        
        # Cap at 95%
        return min(base_confidence + Decimal("60"), Decimal("95"))
    
    def _create_signal(
        self,
        market: Dict,
        probability: Decimal,
        side: str,
        strategy: str,
        confidence: Decimal,
        reasoning: str,
        metadata: Dict = None
    ) -> Signal:
        """Create a signal object"""
        # Calculate position size based on confidence
        base_size = self.config.INITIAL_BANKROLL * (self.config.MAX_POSITION_SIZE_PCT / 100)
        confidence_multiplier = confidence / 100
        suggested_size = base_size * confidence_multiplier
        
        return Signal(
            market_id=market.get("id"),
            market_slug=market.get("slug"),
            market_question=market.get("question"),
            current_probability=probability,
            suggested_side=side,
            suggested_size=suggested_size,
            confidence=confidence,
            strategy=strategy,
            status="pending",
            expires_at=datetime.utcnow() + timedelta(hours=4),
            metadata={
                "reasoning": reasoning,
                **(metadata or {})
            }
        )
    
    async def filter_recent_signals(self, signals: List[Signal]) -> List[Signal]:
        """Filter out signals for markets we recently traded"""
        # Get recent signals from database
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        # This would query the database for recent signals
        # For now, return all signals
        return signals

# Singleton instance
signal_generator = SignalGenerator()
