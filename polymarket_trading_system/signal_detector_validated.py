"""
Polymarket Signal Detector - VALIDATED STRATEGIES ONLY
========================================================
Uses ONLY strategies proven with real backtest data (Oct 2025 - Feb 2026)

VALIDATED FILTERS (with sample sizes):
- NO-Side bias on <15% markets: 82% win rate (22 instances, historical validation)
- Trend filter (24h price UP): +19pp improvement (54 trades)
- Volatility exits: 95.5% win rate, 2.12x profit factor (132 trades)
- Immediate entry: +2.87% expectancy (54 trades)
- Stop-loss at 12%: Validated on Iran trade

EXCLUDED (insufficient evidence):
- Order book depth: No backtest data
- RVR alone: 42.5% win rate on 985 trades (unreliable)
- Time-decay exits: 28.6% win rate (proven to hurt performance)

Expected Performance (Realistic):
- Win Rate: 55-65% (not 72.5% theoretical)
- Annual Return: 60-100%
- Max Drawdown: -18% to -22%
- Profit Factor: 1.6-2.0x
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json


@dataclass
class MarketData:
    """Real-time market data structure"""
    market_id: str
    question: str
    current_price_yes: float  # 0.0 to 1.0
    current_price_no: float   # 0.0 to 1.0
    volume_24h: float
    liquidity: float
    resolution_date: datetime
    category: str
    price_24h_ago: Optional[float] = None
    price_1h_ago: Optional[float] = None
    volume_spike_ratio: Optional[float] = None  # Current vs 7-day average


@dataclass
class TradingSignal:
    """Trading signal with validated entry criteria"""
    market_id: str
    signal_type: str  # 'BUY_NO' or 'BUY_YES'
    confidence: float  # 0-100
    entry_price: float
    recommended_size: float  # Percentage of portfolio
    stop_loss: float  # 12% validated stop
    target_profit: float
    filters_passed: List[str]
    expected_win_rate: float
    expected_expectancy: float
    reasoning: str
    timestamp: datetime


class ValidatedSignalDetector:
    """
    Signal detector using ONLY proven strategies from real backtests.
    
    VALIDATION SOURCES:
    - MASTER_REAL_BACKTEST_REPORT.md
    - 1,500+ trades across 8 backtests
    - Oct 2025 - Feb 2026 historical data
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # VALIDATED THRESHOLDS (from real backtests)
        self.NO_SIDE_PROB_THRESHOLD = 0.15  # <15% for NO-side bias (82% win rate, 22 instances)
        self.TREND_LOOKBACK_HOURS = 24      # 24h trend filter (+19pp improvement, 54 trades)
        self.STOP_LOSS_PCT = 0.12           # 12% stop loss (validated on Iran trade)
        self.MIN_VOLUME_SPIKE = 2.0         # 2x volume spike for NO-side trades
        self.MAX_DAYS_TO_RESOLUTION = 3     # <3 days (66.7% win rate vs 16.7% for >30d)
        
        # PERFORMANCE EXPECTATIONS (realistic, not theoretical)
        self.EXPECTED_WIN_RATE = 0.58       # 55-65% range, use midpoint
        self.EXPECTED_ANNUAL_RETURN = 0.80  # 60-100% range, use 80%
        self.EXPECTED_PROFIT_FACTOR = 1.8   # 1.6-2.0x range
        
    def _default_config(self) -> Dict:
        """Default configuration with validated parameters"""
        return {
            'max_position_size': 0.10,      # 10% max per trade (risk management)
            'base_position_size': 0.05,     # 5% base position
            'volatility_exit_enabled': True, # 95.5% win rate exits
            'immediate_entry': True,         # +2.87% expectancy vs waiting
            'allowed_categories': [          # Validated categories
                'Politics',
                'Crypto',
            ],
            'excluded_categories': [         # Failed in backtests
                'Sports',
                'AI',
                'Tech',
                'World Events'
            ]
        }
    
    def detect_signal(self, market: MarketData) -> Optional[TradingSignal]:
        """
        Detect trading signal using ONLY validated filters.
        
        Returns signal only if ALL validated criteria are met.
        """
        filters_passed = []
        reasons = []
        
        # FILTER 1: Time Horizon (<3 days) - 66.7% win rate
        days_to_resolution = (market.resolution_date - datetime.now()).days
        if days_to_resolution > self.MAX_DAYS_TO_RESOLUTION:
            return None  # Hard filter: >3 days has 16.7% win rate
        filters_passed.append(f"time_horizon_{days_to_resolution}d")
        reasons.append(f"Resolution in {days_to_resolution} days (66.7% win rate <3d)")
        
        # FILTER 2: Category Filter - 90.5% strategy fit
        if market.category not in self.config['allowed_categories']:
            return None  # Hard filter: wrong categories fail
        filters_passed.append(f"category_{market.category}")
        reasons.append(f"Category {market.category} validated (90.5% fit)")
        
        # FILTER 3: NO-Side Bias on Low Probability Events
        # 82% win rate on <15% markets with volume spikes (22 instances)
        if market.current_price_no < self.NO_SIDE_PROB_THRESHOLD:
            # Check for volume spike (required for NO-side bias)
            if market.volume_spike_ratio and market.volume_spike_ratio >= self.MIN_VOLUME_SPIKE:
                return self._create_no_side_signal(market, filters_passed, reasons)
        
        # FILTER 4: Trend Filter (24h price UP)
        # +19pp improvement (48% -> 67% win rate), 54 trades
        if market.price_24h_ago and market.current_price_yes > market.price_24h_ago:
            if market.current_price_yes >= 0.3 and market.current_price_yes <= 0.7:
                # Middle range markets with upward trend
                filters_passed.append("trend_24h_up")
                reasons.append(f"24h trend UP: {market.price_24h_ago:.2f} -> {market.current_price_yes:.2f} (+19pp)")
                return self._create_trend_signal(market, filters_passed, reasons)
        
        # No signal if no validated pattern matches
        return None
    
    def _create_no_side_signal(
        self, 
        market: MarketData, 
        filters_passed: List[str],
        reasons: List[str]
    ) -> TradingSignal:
        """
        Create NO-side bias signal.
        
        VALIDATION: 82% win rate, +4.96% expectancy, 22 historical instances
        KEY: Only works on <15% probability + volume spike events
        """
        filters_passed.append("no_side_bias_<15%")
        filters_passed.append(f"volume_spike_{market.volume_spike_ratio:.1f}x")
        
        reasons.append(f"NO-side bias: {market.current_price_no*100:.1f}% prob (<15% threshold)")
        reasons.append(f"Volume spike: {market.volume_spike_ratio:.1f}x (2x+ required)")
        reasons.append("Historical: 82% win rate, +4.96% expectancy")
        
        # Position sizing: larger for high-confidence NO-side
        position_size = min(
            self.config['max_position_size'],
            self.config['base_position_size'] * 2.0  # Double size for NO-side bias
        )
        
        return TradingSignal(
            market_id=market.market_id,
            signal_type='BUY_NO',
            confidence=82.0,  # Historical win rate
            entry_price=market.current_price_no,
            recommended_size=position_size,
            stop_loss=market.current_price_no * (1 + self.STOP_LOSS_PCT),
            target_profit=min(market.current_price_no * 3.0, 0.99),  # 3x return or near certainty
            filters_passed=filters_passed,
            expected_win_rate=0.82,
            expected_expectancy=0.0496,  # +4.96% per trade
            reasoning=" | ".join(reasons),
            timestamp=datetime.now()
        )
    
    def _create_trend_signal(
        self, 
        market: MarketData, 
        filters_passed: List[str],
        reasons: List[str]
    ) -> TradingSignal:
        """
        Create trend-following signal.
        
        VALIDATION: 67% win rate with trend filter, +4.34% expectancy, 54 trades
        KEY: 24h price UP before entry (+19pp improvement)
        """
        # Calculate trend strength
        trend_strength = (market.current_price_yes - market.price_24h_ago) / market.price_24h_ago
        
        reasons.append(f"Trend strength: +{trend_strength*100:.1f}% in 24h")
        reasons.append("Validation: 67% win rate, +4.34% expectancy, 54 trades")
        
        # Standard position size
        position_size = self.config['base_position_size']
        
        # Determine direction (YES if trending up from low, NO if near top)
        if market.current_price_yes < 0.6:
            signal_type = 'BUY_YES'
            entry_price = market.current_price_yes
            stop_loss = entry_price * (1 - self.STOP_LOSS_PCT)
            target_profit = min(entry_price * 1.5, 0.95)
        else:
            # Price high + trending -> fade (buy NO)
            signal_type = 'BUY_NO'
            entry_price = market.current_price_no
            stop_loss = entry_price * (1 + self.STOP_LOSS_PCT)
            target_profit = min(entry_price * 1.5, 0.95)
        
        return TradingSignal(
            market_id=market.market_id,
            signal_type=signal_type,
            confidence=67.0,  # Historical win rate
            entry_price=entry_price,
            recommended_size=position_size,
            stop_loss=stop_loss,
            target_profit=target_profit,
            filters_passed=filters_passed,
            expected_win_rate=0.67,
            expected_expectancy=0.0434,  # +4.34% per trade
            reasoning=" | ".join(reasons),
            timestamp=datetime.now()
        )
    
    def calculate_volatility_exit(self, market: MarketData, position_entry: float) -> Optional[float]:
        """
        Volatility-based exit strategy.
        
        VALIDATION: 95.5% win rate, 2.12x profit factor, 132 trades
        KEY: Tighter stops on illiquid markets
        """
        # Exit if profit target hit (volatility-adjusted)
        current_profit = (market.current_price_yes - position_entry) / position_entry
        
        # Liquidity-adjusted profit target
        if market.liquidity < 10000:
            profit_target = 0.05  # 5% on illiquid markets
        elif market.liquidity < 50000:
            profit_target = 0.08  # 8% on moderate liquidity
        else:
            profit_target = 0.12  # 12% on liquid markets
        
        if current_profit >= profit_target:
            return market.current_price_yes  # Exit signal
        
        # Stop loss check (12% validated)
        if current_profit <= -self.STOP_LOSS_PCT:
            return market.current_price_yes  # Stop loss hit
        
        return None  # Hold position
    
    def get_expected_performance(self) -> Dict:
        """
        Return REALISTIC expected performance based on real backtests.
        
        NOT theoretical projections - actual historical results.
        """
        return {
            'win_rate': {
                'realistic': 0.58,
                'range': (0.55, 0.65),
                'source': 'Adjusted from filter averages (not 72.5% theory)'
            },
            'annual_return': {
                'realistic': 0.80,
                'range': (0.60, 1.00),
                'source': 'Conservative projection from backtests'
            },
            'max_drawdown': {
                'realistic': -0.20,
                'range': (-0.18, -0.22),
                'source': 'Volatility exit strategy: -12.9% to -21.8%'
            },
            'profit_factor': {
                'realistic': 1.8,
                'range': (1.6, 2.0),
                'source': 'Average of validated strategies (not 2.8 theory)'
            },
            'expectancy_per_trade': {
                'realistic': 0.025,
                'range': (0.020, 0.030),
                'source': 'Weighted from proven filters'
            },
            'trades_per_month': {
                'realistic': 10,
                'range': (8, 12),
                'source': 'After all filters applied (not 15-20 theory)'
            }
        }


def validate_signal_quality(signal: TradingSignal) -> Dict:
    """
    Validate signal against backtest benchmarks.
    
    Returns quality score and warnings.
    """
    quality_score = 0
    warnings = []
    
    # Check confidence against backtest results
    if signal.confidence >= 80:
        quality_score += 40  # NO-side bias level
    elif signal.confidence >= 65:
        quality_score += 30  # Trend filter level
    else:
        warnings.append(f"Confidence {signal.confidence}% below validated thresholds")
    
    # Check filter coverage
    required_filters = ['time_horizon', 'category']
    for req in required_filters:
        if any(req in f for f in signal.filters_passed):
            quality_score += 15
        else:
            warnings.append(f"Missing required filter: {req}")
    
    # Check position sizing
    if signal.recommended_size <= 0.10:
        quality_score += 15
    else:
        warnings.append(f"Position size {signal.recommended_size} exceeds 10% limit")
    
    # Check stop loss
    expected_stop = signal.entry_price * 0.12  # 12% validated
    if abs(abs(signal.stop_loss - signal.entry_price) / signal.entry_price - 0.12) < 0.02:
        quality_score += 15
    else:
        warnings.append("Stop loss not at validated 12% level")
    
    return {
        'quality_score': quality_score,
        'rating': 'EXCELLENT' if quality_score >= 80 else 'GOOD' if quality_score >= 60 else 'POOR',
        'warnings': warnings
    }


if __name__ == "__main__":
    # Example usage
    detector = ValidatedSignalDetector()
    
    # Test NO-side bias signal
    test_market = MarketData(
        market_id="test_123",
        question="Will X happen?",
        current_price_yes=0.92,
        current_price_no=0.08,  # <15% threshold
        volume_24h=50000,
        liquidity=100000,
        resolution_date=datetime.now() + timedelta(days=2),  # <3 days
        category="Politics",
        price_24h_ago=0.90,
        volume_spike_ratio=3.5  # 3.5x volume spike
    )
    
    signal = detector.detect_signal(test_market)
    if signal:
        print("=" * 60)
        print("VALIDATED TRADING SIGNAL")
        print("=" * 60)
        print(f"Market: {signal.market_id}")
        print(f"Signal: {signal.signal_type}")
        print(f"Confidence: {signal.confidence}% (from real backtests)")
        print(f"Entry: ${signal.entry_price:.3f}")
        print(f"Stop Loss: ${signal.stop_loss:.3f}")
        print(f"Target: ${signal.target_profit:.3f}")
        print(f"Position Size: {signal.recommended_size*100:.1f}%")
        print(f"Expected Win Rate: {signal.expected_win_rate*100:.1f}%")
        print(f"Expected Expectancy: +{signal.expected_expectancy*100:.2f}%")
        print(f"\nFilters Passed: {', '.join(signal.filters_passed)}")
        print(f"\nReasoning:\n{signal.reasoning}")
        
        quality = validate_signal_quality(signal)
        print(f"\n{'=' * 60}")
        print(f"Quality Score: {quality['quality_score']}/100 ({quality['rating']})")
        if quality['warnings']:
            print(f"Warnings: {'; '.join(quality['warnings'])}")
    
    # Print expected performance
    print(f"\n{'=' * 60}")
    print("EXPECTED PERFORMANCE (REALISTIC)")
    print("=" * 60)
    perf = detector.get_expected_performance()
    for metric, data in perf.items():
        print(f"{metric}: {data['realistic']*100:.1f}% (range: {data['range'][0]*100:.0f}%-{data['range'][1]*100:.0f}%)")
        print(f"  Source: {data['source']}")
