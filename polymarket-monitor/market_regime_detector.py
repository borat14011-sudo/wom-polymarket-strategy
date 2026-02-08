"""
Market Regime Detector for Crypto
Determines if BTC, ETH, SOL are in BULL, BEAR, or SIDEWAYS market regimes.

Regime Rules:
- BULL: Price up >20% in 30 days
- BEAR: Price down >20% in 30 days  
- SIDEWAYS: Price within ±15% of 30-day average

Used by CRYPTO_FADE_BULL validator to only trade in sideways/bear markets.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics


class MarketRegime(Enum):
    """Market regime classification"""
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"


@dataclass
class RegimeData:
    """Data structure for regime analysis"""
    coin: str
    current_price: float
    regime: MarketRegime
    price_change_7d: float
    price_change_14d: float
    price_change_30d: float
    avg_price_30d: float
    timestamp: datetime


class MarketRegimeDetector:
    """Detects market regimes for major cryptocurrencies"""
    
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    
    # CoinGecko IDs for our coins
    COIN_IDS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana"
    }
    
    def __init__(self, use_fallback: bool = True):
        """
        Initialize the detector.
        
        Args:
            use_fallback: If True, will try CoinMarketCap if CoinGecko fails
        """
        self.use_fallback = use_fallback
        self.cache = {}
        self.cache_time = None
        self.cache_ttl = 300  # 5 minutes cache
    
    def fetch_price_history(self, coin_id: str, days: int = 30) -> List[Tuple[float, float]]:
        """
        Fetch historical price data from CoinGecko.
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of history to fetch
            
        Returns:
            List of (timestamp, price) tuples
        """
        url = f"{self.COINGECKO_API}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # CoinGecko returns prices as [[timestamp_ms, price], ...]
            prices = [(ts / 1000, price) for ts, price in data.get("prices", [])]
            return prices
            
        except Exception as e:
            print(f"Error fetching {coin_id} from CoinGecko: {e}")
            return []
    
    def fetch_current_price(self, coin_id: str) -> float:
        """
        Fetch current price from CoinGecko.
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Current price in USD
        """
        url = f"{self.COINGECKO_API}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[coin_id]["usd"]
            
        except Exception as e:
            print(f"Error fetching current price for {coin_id}: {e}")
            return 0.0
    
    def calculate_price_change(self, prices: List[Tuple[float, float]], days: int) -> float:
        """
        Calculate percentage price change over a period.
        
        Args:
            prices: List of (timestamp, price) tuples
            days: Number of days to look back
            
        Returns:
            Percentage change (e.g., 25.5 for +25.5%)
        """
        if not prices or len(prices) < 2:
            return 0.0
        
        current_price = prices[-1][1]
        
        # Find price closest to N days ago
        target_timestamp = prices[-1][0] - (days * 86400)
        old_price = min(prices, key=lambda x: abs(x[0] - target_timestamp))[1]
        
        if old_price == 0:
            return 0.0
        
        change = ((current_price - old_price) / old_price) * 100
        return round(change, 2)
    
    def calculate_average_price(self, prices: List[Tuple[float, float]]) -> float:
        """
        Calculate average price over the period.
        
        Args:
            prices: List of (timestamp, price) tuples
            
        Returns:
            Average price
        """
        if not prices:
            return 0.0
        
        price_values = [price for _, price in prices]
        return statistics.mean(price_values)
    
    def determine_regime(self, price_change_30d: float, current_price: float, avg_price_30d: float) -> MarketRegime:
        """
        Determine market regime based on price changes.
        
        Rules:
        - BULL: Price up >20% in 30 days
        - BEAR: Price down >20% in 30 days
        - SIDEWAYS: Price within ±15% of 30-day average
        
        Args:
            price_change_30d: 30-day price change percentage
            current_price: Current price
            avg_price_30d: 30-day average price
            
        Returns:
            MarketRegime enum
        """
        # First check 30-day trend
        if price_change_30d > 20:
            return MarketRegime.BULL
        elif price_change_30d < -20:
            return MarketRegime.BEAR
        
        # If not clearly bull or bear, check if sideways
        # Calculate deviation from 30-day average
        if avg_price_30d > 0:
            deviation = ((current_price - avg_price_30d) / avg_price_30d) * 100
            if -15 <= deviation <= 15:
                return MarketRegime.SIDEWAYS
        
        # Default to sideways if within range but not extreme
        if -20 <= price_change_30d <= 20:
            return MarketRegime.SIDEWAYS
        
        # Edge case: if we get here, classify based on sign
        return MarketRegime.BULL if price_change_30d > 0 else MarketRegime.BEAR
    
    def get_regime_data(self, coin: str) -> RegimeData:
        """
        Get regime data for a specific coin.
        
        Args:
            coin: Coin symbol (BTC, ETH, SOL)
            
        Returns:
            RegimeData object with analysis
        """
        coin_id = self.COIN_IDS.get(coin.upper())
        if not coin_id:
            raise ValueError(f"Unknown coin: {coin}")
        
        # Fetch 30 days of price history
        prices = self.fetch_price_history(coin_id, days=30)
        
        if not prices:
            raise Exception(f"Failed to fetch price data for {coin}")
        
        current_price = prices[-1][1]
        
        # Calculate price changes
        price_change_7d = self.calculate_price_change(prices, 7)
        price_change_14d = self.calculate_price_change(prices, 14)
        price_change_30d = self.calculate_price_change(prices, 30)
        
        # Calculate 30-day average
        avg_price_30d = self.calculate_average_price(prices)
        
        # Determine regime
        regime = self.determine_regime(price_change_30d, current_price, avg_price_30d)
        
        return RegimeData(
            coin=coin.upper(),
            current_price=current_price,
            regime=regime,
            price_change_7d=price_change_7d,
            price_change_14d=price_change_14d,
            price_change_30d=price_change_30d,
            avg_price_30d=avg_price_30d,
            timestamp=datetime.now()
        )
    
    def get_all_regimes(self) -> Dict[str, RegimeData]:
        """
        Get regime data for all tracked coins.
        
        Returns:
            Dictionary mapping coin symbols to RegimeData
        """
        # Check cache
        if self.cache_time and (datetime.now() - self.cache_time).total_seconds() < self.cache_ttl:
            return self.cache
        
        regimes = {}
        for coin in self.COIN_IDS.keys():
            try:
                regimes[coin] = self.get_regime_data(coin)
            except Exception as e:
                print(f"Error getting regime for {coin}: {e}")
        
        # Update cache
        self.cache = regimes
        self.cache_time = datetime.now()
        
        return regimes
    
    def is_tradeable_regime(self, coin: str) -> bool:
        """
        Check if coin is in a tradeable regime for CRYPTO_FADE_BULL strategy.
        
        Strategy only trades in SIDEWAYS or BEAR markets (fades bull sentiment).
        
        Args:
            coin: Coin symbol (BTC, ETH, SOL)
            
        Returns:
            True if in SIDEWAYS or BEAR regime
        """
        try:
            regime_data = self.get_regime_data(coin)
            return regime_data.regime in [MarketRegime.SIDEWAYS, MarketRegime.BEAR]
        except Exception as e:
            print(f"Error checking tradeable regime for {coin}: {e}")
            return False
    
    def get_market_summary(self) -> str:
        """
        Get a formatted summary of all market regimes.
        
        Returns:
            String summary of current market regimes
        """
        regimes = self.get_all_regimes()
        
        if not regimes:
            return "⚠️ Unable to fetch market regime data"
        
        lines = ["📊 Crypto Market Regime Summary", ""]
        
        for coin, data in regimes.items():
            emoji = {
                MarketRegime.BULL: "🟢",
                MarketRegime.BEAR: "🔴",
                MarketRegime.SIDEWAYS: "🟡"
            }.get(data.regime, "⚪")
            
            lines.append(f"{emoji} **{coin}**: {data.regime.value}")
            lines.append(f"   Price: ${data.current_price:,.2f}")
            lines.append(f"   7d: {data.price_change_7d:+.1f}% | 14d: {data.price_change_14d:+.1f}% | 30d: {data.price_change_30d:+.1f}%")
            lines.append(f"   30d Avg: ${data.avg_price_30d:,.2f}")
            lines.append("")
        
        # Add trading recommendation
        tradeable = [coin for coin, data in regimes.items() 
                    if data.regime in [MarketRegime.SIDEWAYS, MarketRegime.BEAR]]
        
        if tradeable:
            lines.append(f"✅ Tradeable (FADE_BULL): {', '.join(tradeable)}")
        else:
            lines.append("🚫 No tradeable regimes (all BULL)")
        
        return "\n".join(lines)


# Convenience functions for quick checks
def get_detector() -> MarketRegimeDetector:
    """Get a detector instance"""
    return MarketRegimeDetector()


def check_regime(coin: str) -> MarketRegime:
    """
    Quick check of market regime for a coin.
    
    Args:
        coin: Coin symbol (BTC, ETH, SOL)
        
    Returns:
        MarketRegime enum
    """
    detector = get_detector()
    data = detector.get_regime_data(coin)
    return data.regime


def is_tradeable(coin: str) -> bool:
    """
    Quick check if coin is tradeable for CRYPTO_FADE_BULL.
    
    Args:
        coin: Coin symbol (BTC, ETH, SOL)
        
    Returns:
        True if in SIDEWAYS or BEAR regime
    """
    detector = get_detector()
    return detector.is_tradeable_regime(coin)


if __name__ == "__main__":
    # Example usage
    detector = MarketRegimeDetector()
    
    print("Fetching market regimes...\n")
    print(detector.get_market_summary())
    
    print("\n" + "="*50)
    print("Individual Checks:")
    print("="*50 + "\n")
    
    for coin in ["BTC", "ETH", "SOL"]:
        try:
            data = detector.get_regime_data(coin)
            tradeable = "✅ TRADEABLE" if detector.is_tradeable_regime(coin) else "🚫 NOT TRADEABLE"
            print(f"{coin}: {data.regime.value} ({data.price_change_30d:+.1f}% 30d) - {tradeable}")
        except Exception as e:
            print(f"{coin}: Error - {e}")
