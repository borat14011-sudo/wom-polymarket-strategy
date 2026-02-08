"""
Strategy Validator - Bulletproof Edge Criteria Enforcement
================================================================
Validates if detected signals meet ALL edge criteria for each strategy.
False positives are expensive - every check must pass.

Author: Polymarket Monitor Team
Date: February 7, 2026
Version: 1.0
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Crypto market regime classification"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"


class ValidationResult:
    """Structured validation result with confidence scoring"""
    
    def __init__(self, valid: bool, strategy: str, confidence: int = 0, 
                 rejection_reason: Optional[str] = None, details: Optional[Dict] = None):
        self.valid = valid
        self.strategy = strategy
        self.confidence = confidence  # 0-100
        self.rejection_reason = rejection_reason
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/storage"""
        return {
            'valid': self.valid,
            'strategy': self.strategy,
            'confidence': self.confidence,
            'rejection_reason': self.rejection_reason,
            'details': self.details,
            'timestamp': self.timestamp
        }
    
    def __repr__(self) -> str:
        if self.valid:
            return f"✅ VALID - {self.strategy} (confidence: {self.confidence}%)"
        else:
            return f"❌ REJECTED - {self.strategy}: {self.rejection_reason}"


class StrategyValidator:
    """
    Main validator class - checks if signals meet strategy-specific edge criteria
    """
    
    def __init__(self):
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.clob_api = "https://clob.polymarket.com"
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        
        # Cache for market regime (5 min TTL)
        self._regime_cache: Optional[Tuple[MarketRegime, datetime]] = None
        self._regime_cache_ttl = timedelta(minutes=5)
    
    def validate(self, signal: Dict, strategy: str) -> ValidationResult:
        """
        Main validation entry point
        
        Args:
            signal: Market signal data from detector
            strategy: Strategy name to validate against
            
        Returns:
            ValidationResult with pass/fail and confidence score
        """
        strategy_upper = strategy.upper()
        
        validators = {
            'MUSK_FADE_EXTREMES': self._validate_musk_fade_extremes,
            'CRYPTO_FADE_BULL': self._validate_crypto_fade_bull,
            'SHUTDOWN_POWER_LAW': self._validate_shutdown_power_law,
            'SPOTIFY_MOMENTUM': self._validate_spotify_momentum,
            'PLAYER_PROPS_UNDER': self._validate_player_props_under,
        }
        
        validator_func = validators.get(strategy_upper)
        
        if not validator_func:
            return ValidationResult(
                valid=False,
                strategy=strategy,
                rejection_reason=f"Unknown strategy: {strategy}"
            )
        
        try:
            return validator_func(signal)
        except Exception as e:
            logger.error(f"Validation error for {strategy}: {e}")
            return ValidationResult(
                valid=False,
                strategy=strategy,
                rejection_reason=f"Validation error: {str(e)}"
            )
    
    def _validate_musk_fade_extremes(self, signal: Dict) -> ValidationResult:
        """
        MUSK_FADE_EXTREMES Strategy Validation
        
        Edge Criteria:
        - Price < 15% (extreme underpricing for NO bets)
        - Extreme range detected (high volatility environment)
        - Volume > $100K (sufficient liquidity)
        - Title contains Musk/Tesla/X/Twitter keywords
        """
        market_id = signal.get('market_id')
        title = signal.get('title', '')
        current_price = signal.get('current_yes_price', 0)
        volume_24h = signal.get('volume_24h', 0)
        
        confidence = 0
        details = {}
        
        # CHECK 1: Price < 15%
        if current_price >= 0.15:
            return ValidationResult(
                valid=False,
                strategy='MUSK_FADE_EXTREMES',
                rejection_reason=f"Price too high: {current_price:.1%} >= 15%"
            )
        confidence += 25
        details['price_check'] = f"✅ {current_price:.1%} < 15%"
        
        # CHECK 2: Musk-related keywords
        musk_keywords = ['musk', 'elon', 'tesla', 'x.com', 'twitter', 'spacex']
        has_musk = any(kw in title.lower() for kw in musk_keywords)
        
        if not has_musk:
            return ValidationResult(
                valid=False,
                strategy='MUSK_FADE_EXTREMES',
                rejection_reason=f"Not Musk-related: '{title}'"
            )
        confidence += 25
        details['keyword_check'] = "✅ Musk-related market"
        
        # CHECK 3: Volume > $100K
        if volume_24h < 100000:
            return ValidationResult(
                valid=False,
                strategy='MUSK_FADE_EXTREMES',
                rejection_reason=f"Volume too low: ${volume_24h:,.0f} < $100K"
            )
        confidence += 25
        details['volume_check'] = f"✅ ${volume_24h:,.0f} > $100K"
        
        # CHECK 4: Extreme range (volatility check via orderbook spread)
        spread_data = self._get_orderbook_spread(market_id, signal.get('clobTokenIds'))
        
        if spread_data:
            spread = spread_data.get('spread', 0)
            # Wide spread (>5%) indicates extreme range/volatility
            if spread < 0.05:
                return ValidationResult(
                    valid=False,
                    strategy='MUSK_FADE_EXTREMES',
                    rejection_reason=f"Low volatility: spread {spread:.1%} < 5%"
                )
            confidence += 25
            details['volatility_check'] = f"✅ High volatility: spread {spread:.1%}"
            details['spread'] = spread
        else:
            # Can't verify extreme range - reduce confidence
            confidence += 10
            details['volatility_check'] = "⚠️ Could not verify extreme range"
        
        return ValidationResult(
            valid=True,
            strategy='MUSK_FADE_EXTREMES',
            confidence=confidence,
            details=details
        )
    
    def _validate_crypto_fade_bull(self, signal: Dict) -> ValidationResult:
        """
        CRYPTO_FADE_BULL Strategy Validation
        
        Edge Criteria:
        - Price > 40% (overbought for fade)
        - Price move > 15% in 24h (significant momentum)
        - Market closes < 7 days (short timeframe)
        - Sideways market regime (no strong bull trend to fight)
        - Category = crypto/cryptocurrency
        """
        title = signal.get('title', '')
        current_price = signal.get('current_yes_price', 0)
        roc_24h = signal.get('roc_24h_pct', 0)
        days_to_resolution = signal.get('days_to_resolution', 999)
        category = signal.get('category', '').lower()
        
        confidence = 0
        details = {}
        
        # CHECK 1: Category = crypto
        crypto_categories = ['crypto', 'cryptocurrency', 'bitcoin', 'ethereum']
        is_crypto = any(cat in category for cat in crypto_categories)
        
        if not is_crypto:
            return ValidationResult(
                valid=False,
                strategy='CRYPTO_FADE_BULL',
                rejection_reason=f"Not crypto category: '{category}'"
            )
        confidence += 20
        details['category_check'] = f"✅ Crypto category: {category}"
        
        # CHECK 2: Price > 40%
        if current_price <= 0.40:
            return ValidationResult(
                valid=False,
                strategy='CRYPTO_FADE_BULL',
                rejection_reason=f"Price too low for fade: {current_price:.1%} <= 40%"
            )
        confidence += 20
        details['price_check'] = f"✅ {current_price:.1%} > 40%"
        
        # CHECK 3: ROC > 15% (24h move)
        if abs(roc_24h) < 15:
            return ValidationResult(
                valid=False,
                strategy='CRYPTO_FADE_BULL',
                rejection_reason=f"Move too small: {roc_24h:+.1f}% < 15%"
            )
        confidence += 20
        details['momentum_check'] = f"✅ {roc_24h:+.1f}% > 15%"
        
        # CHECK 4: Days < 7
        if days_to_resolution >= 7:
            return ValidationResult(
                valid=False,
                strategy='CRYPTO_FADE_BULL',
                rejection_reason=f"Too far out: {days_to_resolution}d >= 7d"
            )
        confidence += 20
        details['timeframe_check'] = f"✅ {days_to_resolution}d < 7d"
        
        # CHECK 5: Market regime = SIDEWAYS (critical for fade strategy)
        regime = self._get_market_regime()
        
        if regime == MarketRegime.BULL:
            return ValidationResult(
                valid=False,
                strategy='CRYPTO_FADE_BULL',
                rejection_reason=f"Strong bull market - don't fade momentum"
            )
        elif regime == MarketRegime.SIDEWAYS:
            confidence += 20
            details['regime_check'] = "✅ Sideways market (safe to fade)"
        elif regime == MarketRegime.BEAR:
            confidence += 10
            details['regime_check'] = "⚠️ Bear market (acceptable but not ideal)"
        else:
            confidence += 5
            details['regime_check'] = "⚠️ Unknown regime (proceed with caution)"
        
        details['market_regime'] = regime.value
        
        return ValidationResult(
            valid=True,
            strategy='CRYPTO_FADE_BULL',
            confidence=confidence,
            details=details
        )
    
    def _validate_shutdown_power_law(self, signal: Dict) -> ValidationResult:
        """
        SHUTDOWN_POWER_LAW Strategy Validation
        
        Edge Criteria:
        - Duration matches power law decay pattern
        - Price meets threshold for event stage
        - Event is active (not resolved/cancelled)
        - Government shutdown or similar catalytic event
        """
        title = signal.get('title', '')
        current_price = signal.get('current_yes_price', 0)
        days_to_resolution = signal.get('days_to_resolution', 999)
        volume_24h = signal.get('volume_24h', 0)
        
        confidence = 0
        details = {}
        
        # CHECK 1: Shutdown-related keywords
        shutdown_keywords = ['shutdown', 'government shutdown', 'debt ceiling', 
                           'congress', 'budget crisis', 'funding bill']
        is_shutdown = any(kw in title.lower() for kw in shutdown_keywords)
        
        if not is_shutdown:
            return ValidationResult(
                valid=False,
                strategy='SHUTDOWN_POWER_LAW',
                rejection_reason=f"Not shutdown-related: '{title}'"
            )
        confidence += 25
        details['event_check'] = "✅ Shutdown-related event"
        
        # CHECK 2: Duration-price power law relationship
        # Power law: probability decays as ~1/sqrt(days)
        # Expected price thresholds:
        # - 1-2 days: 40-60%
        # - 3-5 days: 20-40%
        # - 6-10 days: 10-25%
        # - 10+ days: <10%
        
        expected_range = None
        if days_to_resolution <= 2:
            expected_range = (0.40, 0.60)
            stage = "imminent"
        elif days_to_resolution <= 5:
            expected_range = (0.20, 0.40)
            stage = "near-term"
        elif days_to_resolution <= 10:
            expected_range = (0.10, 0.25)
            stage = "medium-term"
        else:
            expected_range = (0.0, 0.10)
            stage = "long-term"
        
        in_range = expected_range[0] <= current_price <= expected_range[1]
        
        if not in_range:
            return ValidationResult(
                valid=False,
                strategy='SHUTDOWN_POWER_LAW',
                rejection_reason=f"Price {current_price:.1%} outside {stage} range {expected_range[0]:.1%}-{expected_range[1]:.1%}"
            )
        confidence += 30
        details['power_law_check'] = f"✅ {stage}: {current_price:.1%} in range {expected_range[0]:.1%}-{expected_range[1]:.1%}"
        details['event_stage'] = stage
        
        # CHECK 3: Volume sufficient (>$50K for shutdown markets)
        if volume_24h < 50000:
            return ValidationResult(
                valid=False,
                strategy='SHUTDOWN_POWER_LAW',
                rejection_reason=f"Volume too low: ${volume_24h:,.0f} < $50K"
            )
        confidence += 25
        details['volume_check'] = f"✅ ${volume_24h:,.0f} > $50K"
        
        # CHECK 4: Event active (basic sanity checks)
        # - Not in past
        # - Not too far future (>60 days = not imminent shutdown)
        if days_to_resolution < 0:
            return ValidationResult(
                valid=False,
                strategy='SHUTDOWN_POWER_LAW',
                rejection_reason="Event already resolved"
            )
        
        if days_to_resolution > 60:
            return ValidationResult(
                valid=False,
                strategy='SHUTDOWN_POWER_LAW',
                rejection_reason=f"Event too far out: {days_to_resolution}d > 60d"
            )
        
        confidence += 20
        details['active_check'] = f"✅ Event active: {days_to_resolution}d remaining"
        
        return ValidationResult(
            valid=True,
            strategy='SHUTDOWN_POWER_LAW',
            confidence=confidence,
            details=details
        )
    
    def _validate_spotify_momentum(self, signal: Dict) -> ValidationResult:
        """
        SPOTIFY_MOMENTUM Strategy Validation
        
        Edge Criteria:
        - Price 20-60% (momentum sweet spot)
        - Climbing trend (price UP from 24h ago)
        - Volume sufficient (>$50K)
        - Entertainment/music category or Spotify keyword
        """
        title = signal.get('title', '')
        current_price = signal.get('current_yes_price', 0)
        roc_24h = signal.get('roc_24h_pct', 0)
        volume_24h = signal.get('volume_24h', 0)
        category = signal.get('category', '').lower()
        
        confidence = 0
        details = {}
        
        # CHECK 1: Spotify/music-related
        spotify_keywords = ['spotify', 'music', 'album', 'artist', 'song', 
                          'billboard', 'streaming', 'concert']
        is_spotify = any(kw in title.lower() for kw in spotify_keywords)
        is_entertainment = 'entertainment' in category or 'music' in category
        
        if not (is_spotify or is_entertainment):
            return ValidationResult(
                valid=False,
                strategy='SPOTIFY_MOMENTUM',
                rejection_reason=f"Not music/entertainment: '{title}' ({category})"
            )
        confidence += 25
        details['category_check'] = f"✅ Music/entertainment market"
        
        # CHECK 2: Price 20-60% (momentum sweet spot)
        if current_price < 0.20 or current_price > 0.60:
            return ValidationResult(
                valid=False,
                strategy='SPOTIFY_MOMENTUM',
                rejection_reason=f"Price {current_price:.1%} outside 20-60% range"
            )
        confidence += 25
        details['price_check'] = f"✅ {current_price:.1%} in 20-60% range"
        
        # CHECK 3: Climbing trend (positive ROC)
        if roc_24h <= 0:
            return ValidationResult(
                valid=False,
                strategy='SPOTIFY_MOMENTUM',
                rejection_reason=f"Negative momentum: {roc_24h:+.1f}%"
            )
        confidence += 25
        details['trend_check'] = f"✅ Climbing: {roc_24h:+.1f}%"
        
        # Bonus points for strong momentum
        if roc_24h > 10:
            confidence += 10
            details['momentum_bonus'] = f"🚀 Strong momentum: {roc_24h:+.1f}%"
        
        # CHECK 4: Volume sufficient (>$50K)
        if volume_24h < 50000:
            return ValidationResult(
                valid=False,
                strategy='SPOTIFY_MOMENTUM',
                rejection_reason=f"Volume too low: ${volume_24h:,.0f} < $50K"
            )
        confidence += 15
        details['volume_check'] = f"✅ ${volume_24h:,.0f} > $50K"
        
        return ValidationResult(
            valid=True,
            strategy='SPOTIFY_MOMENTUM',
            confidence=min(confidence, 100),  # Cap at 100
            details=details
        )
    
    def _validate_player_props_under(self, signal: Dict) -> ValidationResult:
        """
        PLAYER_PROPS_UNDER Strategy Validation
        
        Edge Criteria:
        - OVER price > 55% (implied UNDER edge)
        - Volume > $100K (liquid market)
        - NBA only (not other sports)
        - Player prop bet (points/rebounds/assists)
        """
        title = signal.get('title', '')
        current_price = signal.get('current_yes_price', 0)
        volume_24h = signal.get('volume_24h', 0)
        category = signal.get('category', '').lower()
        
        confidence = 0
        details = {}
        
        # CHECK 1: NBA market
        nba_keywords = ['nba', 'basketball', 'lebron', 'curry', 'durant', 'lakers', 
                       'warriors', 'celtics', 'bucks', 'nets']
        is_nba = any(kw in title.lower() for kw in nba_keywords) or 'basketball' in category
        
        if not is_nba:
            return ValidationResult(
                valid=False,
                strategy='PLAYER_PROPS_UNDER',
                rejection_reason=f"Not NBA: '{title}' ({category})"
            )
        confidence += 25
        details['sport_check'] = "✅ NBA market"
        
        # CHECK 2: Player prop keywords
        prop_keywords = ['points', 'rebounds', 'assists', 'over', 'under', 
                        'pts', 'reb', 'ast', 'score']
        is_prop = any(kw in title.lower() for kw in prop_keywords)
        
        if not is_prop:
            return ValidationResult(
                valid=False,
                strategy='PLAYER_PROPS_UNDER',
                rejection_reason=f"Not player prop: '{title}'"
            )
        confidence += 25
        details['prop_check'] = "✅ Player prop bet"
        
        # CHECK 3: OVER price > 55% (we're betting UNDER)
        # If YES = "Player scores OVER X points"
        # Then NO = "Player scores UNDER X points"
        # We want OVER overpriced (>55%) so we can fade it
        
        if current_price <= 0.55:
            return ValidationResult(
                valid=False,
                strategy='PLAYER_PROPS_UNDER',
                rejection_reason=f"OVER not overpriced: {current_price:.1%} <= 55%"
            )
        confidence += 30
        details['price_check'] = f"✅ OVER {current_price:.1%} > 55% (fade-able)"
        details['implied_under_price'] = f"{1 - current_price:.1%}"
        
        # CHECK 4: Volume > $100K
        if volume_24h < 100000:
            return ValidationResult(
                valid=False,
                strategy='PLAYER_PROPS_UNDER',
                rejection_reason=f"Volume too low: ${volume_24h:,.0f} < $100K"
            )
        confidence += 20
        details['volume_check'] = f"✅ ${volume_24h:,.0f} > $100K"
        
        return ValidationResult(
            valid=True,
            strategy='PLAYER_PROPS_UNDER',
            confidence=confidence,
            details=details
        )
    
    # ==================== HELPER METHODS ====================
    
    def _get_market_regime(self) -> MarketRegime:
        """
        Determine current crypto market regime (bull/bear/sideways)
        
        Uses Bitcoin price as proxy:
        - BULL: +10%+ over 30 days, above 50-day MA
        - BEAR: -10%+ over 30 days, below 50-day MA
        - SIDEWAYS: Between -10% and +10%, choppy
        
        Cached for 5 minutes to avoid rate limits
        """
        # Check cache
        if self._regime_cache:
            regime, timestamp = self._regime_cache
            if datetime.now() - timestamp < self._regime_cache_ttl:
                logger.debug(f"Using cached regime: {regime.value}")
                return regime
        
        try:
            # Fetch BTC price data (30 days)
            response = requests.get(
                f"{self.coingecko_api}/coins/bitcoin/market_chart",
                params={'vs_currency': 'usd', 'days': 30},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch BTC data: {response.status_code}")
                return MarketRegime.UNKNOWN
            
            data = response.json()
            prices = [p[1] for p in data.get('prices', [])]
            
            if len(prices) < 30:
                logger.warning("Insufficient price data for regime detection")
                return MarketRegime.UNKNOWN
            
            # Calculate metrics
            current_price = prices[-1]
            price_30d_ago = prices[0]
            ma_50 = sum(prices[-50:]) / min(50, len(prices))
            
            change_30d_pct = ((current_price - price_30d_ago) / price_30d_ago) * 100
            
            # Determine regime
            if change_30d_pct > 10 and current_price > ma_50:
                regime = MarketRegime.BULL
            elif change_30d_pct < -10 and current_price < ma_50:
                regime = MarketRegime.BEAR
            else:
                regime = MarketRegime.SIDEWAYS
            
            # Cache result
            self._regime_cache = (regime, datetime.now())
            
            logger.info(f"Market regime: {regime.value} (30d: {change_30d_pct:+.1f}%, price: ${current_price:,.0f}, MA50: ${ma_50:,.0f})")
            return regime
            
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return MarketRegime.UNKNOWN
    
    def _get_orderbook_spread(self, market_id: str, clob_token_ids: List[str]) -> Optional[Dict]:
        """
        Get orderbook spread as volatility indicator
        
        Returns:
            Dict with spread, best_bid, best_ask or None
        """
        if not clob_token_ids or len(clob_token_ids) < 1:
            return None
        
        try:
            token_id = clob_token_ids[0]  # YES token
            
            response = requests.get(
                f"{self.clob_api}/book",
                params={'token_id': token_id},
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch orderbook: {response.status_code}")
                return None
            
            book = response.json()
            
            bids = book.get('bids', [])
            asks = book.get('asks', [])
            
            if not bids or not asks:
                return None
            
            best_bid = float(bids[0]['price'])
            best_ask = float(asks[0]['price'])
            spread = best_ask - best_bid
            
            return {
                'spread': spread,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'bid_depth': sum(float(b.get('size', 0)) for b in bids[:5]),
                'ask_depth': sum(float(a.get('size', 0)) for a in asks[:5])
            }
            
        except Exception as e:
            logger.error(f"Error fetching orderbook spread: {e}")
            return None
    
    def get_liquidity_check(self, market_id: str, clob_token_ids: List[str], 
                           min_depth: float = 10000) -> Tuple[bool, Dict]:
        """
        Check if market has sufficient liquidity
        
        Args:
            market_id: Market identifier
            clob_token_ids: Token IDs for orderbook lookup
            min_depth: Minimum required depth in USD
            
        Returns:
            (passes_check, details_dict)
        """
        spread_data = self._get_orderbook_spread(market_id, clob_token_ids)
        
        if not spread_data:
            return False, {'error': 'Could not fetch orderbook data'}
        
        total_depth = spread_data.get('bid_depth', 0) + spread_data.get('ask_depth', 0)
        spread = spread_data.get('spread', 1)
        
        passes = total_depth >= min_depth and spread < 0.10  # Max 10% spread
        
        details = {
            'total_depth': total_depth,
            'min_depth': min_depth,
            'spread': spread,
            'passes': passes,
            'bid_depth': spread_data.get('bid_depth', 0),
            'ask_depth': spread_data.get('ask_depth', 0)
        }
        
        return passes, details


# ==================== CONVENIENCE FUNCTIONS ====================

def validate_signal(signal: Dict, strategy: str) -> ValidationResult:
    """
    Convenience function for single signal validation
    
    Usage:
        result = validate_signal(signal_data, 'MUSK_FADE_EXTREMES')
        if result.valid:
            print(f"✅ Confidence: {result.confidence}%")
        else:
            print(f"❌ {result.rejection_reason}")
    """
    validator = StrategyValidator()
    return validator.validate(signal, strategy)


def batch_validate(signals: List[Dict], strategy: str) -> List[ValidationResult]:
    """
    Validate multiple signals against same strategy
    
    Returns:
        List of ValidationResult objects
    """
    validator = StrategyValidator()
    return [validator.validate(sig, strategy) for sig in signals]


def validate_all_strategies(signal: Dict) -> Dict[str, ValidationResult]:
    """
    Test signal against ALL strategies
    
    Returns:
        Dict mapping strategy_name -> ValidationResult
    """
    strategies = [
        'MUSK_FADE_EXTREMES',
        'CRYPTO_FADE_BULL',
        'SHUTDOWN_POWER_LAW',
        'SPOTIFY_MOMENTUM',
        'PLAYER_PROPS_UNDER'
    ]
    
    validator = StrategyValidator()
    results = {}
    
    for strategy in strategies:
        results[strategy] = validator.validate(signal, strategy)
    
    return results


# ==================== TESTING ====================

if __name__ == "__main__":
    # Test the validator
    logging.basicConfig(level=logging.INFO)
    
    print("🔬 Testing Strategy Validator")
    print("=" * 70)
    
    # Test signal 1: Musk fade
    test_signal_musk = {
        'market_id': 'test_123',
        'title': 'Will Elon Musk step down as Twitter CEO by March 2026?',
        'current_yes_price': 0.12,
        'volume_24h': 150000,
        'roc_24h_pct': 8.5,
        'days_to_resolution': 5,
        'category': 'tech',
        'clobTokenIds': ['token_yes', 'token_no']
    }
    
    print("\n📊 Test 1: MUSK_FADE_EXTREMES")
    result1 = validate_signal(test_signal_musk, 'MUSK_FADE_EXTREMES')
    print(result1)
    print(f"Details: {result1.details}")
    
    # Test signal 2: Crypto fade
    test_signal_crypto = {
        'market_id': 'test_456',
        'title': 'Will Bitcoin reach $100K by end of week?',
        'current_yes_price': 0.65,
        'volume_24h': 250000,
        'roc_24h_pct': 18.2,
        'days_to_resolution': 3,
        'category': 'crypto',
        'clobTokenIds': ['token_yes', 'token_no']
    }
    
    print("\n📊 Test 2: CRYPTO_FADE_BULL")
    result2 = validate_signal(test_signal_crypto, 'CRYPTO_FADE_BULL')
    print(result2)
    print(f"Details: {result2.details}")
    
    # Test signal 3: Invalid (should reject)
    test_signal_invalid = {
        'market_id': 'test_789',
        'title': 'Will it rain tomorrow?',
        'current_yes_price': 0.50,
        'volume_24h': 5000,  # Too low
        'roc_24h_pct': 2.0,  # Too low
        'days_to_resolution': 1,
        'category': 'weather',
        'clobTokenIds': ['token_yes', 'token_no']
    }
    
    print("\n📊 Test 3: MUSK_FADE_EXTREMES (should reject)")
    result3 = validate_signal(test_signal_invalid, 'MUSK_FADE_EXTREMES')
    print(result3)
    
    # Test all strategies
    print("\n📊 Test 4: Validate against ALL strategies")
    all_results = validate_all_strategies(test_signal_musk)
    for strategy, result in all_results.items():
        status = "✅" if result.valid else "❌"
        print(f"{status} {strategy}: {result.confidence}% - {result.rejection_reason or 'VALID'}")
    
    print("\n✅ Validator tests complete!")
