"""
Kelly Criterion Position Sizing Calculator for Polymarket Trading

Calculates optimal position sizes using Kelly Criterion with Quarter-Kelly adjustment
and enforces risk management limits.

Kelly Formula: f* = (p * b - q) / b
Where:
    p = probability of winning (win rate)
    q = probability of losing (1 - p)
    b = net odds (for binary markets: (1/price) - 1)
    
Quarter-Kelly: Use f*/4 for more conservative sizing
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk level indicators"""
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    BLOCKED = "BLOCKED"


@dataclass
class Position:
    """Represents an existing position"""
    market_id: str
    size: float  # in USDC
    strategy: str


@dataclass
class PositionRecommendation:
    """Position sizing recommendation with risk assessment"""
    strategy: str
    recommended_size_usdc: float
    recommended_pct: float
    kelly_fraction: float
    quarter_kelly_pct: float
    current_exposure_pct: float
    total_exposure_after_pct: float
    risk_level: RiskLevel
    warnings: List[str]
    can_trade: bool
    
    def __str__(self) -> str:
        """Pretty print recommendation"""
        lines = [
            f"\n{'='*60}",
            f"POSITION SIZE RECOMMENDATION - {self.strategy}",
            f"{'='*60}",
            f"💰 Recommended Size: ${self.recommended_size_usdc:,.2f} USDC ({self.recommended_pct:.2f}%)",
            f"📊 Kelly Fraction: {self.kelly_fraction:.4f} → Quarter-Kelly: {self.quarter_kelly_pct:.2f}%",
            f"📈 Current Exposure: {self.current_exposure_pct:.2f}%",
            f"📊 Total After Trade: {self.total_exposure_after_pct:.2f}%",
            f"⚠️  Risk Level: {self.risk_level.value}",
        ]
        
        if self.warnings:
            lines.append(f"\n⚠️  WARNINGS:")
            for warning in self.warnings:
                lines.append(f"   • {warning}")
        
        if self.can_trade:
            lines.append(f"\n✅ TRADE APPROVED")
        else:
            lines.append(f"\n🚫 TRADE BLOCKED - Risk limits exceeded")
        
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)


class PositionSizer:
    """Kelly Criterion Position Sizer with risk management"""
    
    # Risk limits
    MAX_SINGLE_POSITION_PCT = 6.25  # Max 6.25% per position
    MAX_TOTAL_EXPOSURE_PCT = 25.0   # Max 25% total exposure
    
    # Kelly adjustment factor
    KELLY_FRACTION = 0.25  # Quarter-Kelly for conservative sizing
    
    def __init__(self, bankroll: float):
        """
        Initialize position sizer
        
        Args:
            bankroll: Current account balance in USDC
        """
        if bankroll <= 0:
            raise ValueError("Bankroll must be positive")
        self.bankroll = bankroll
    
    def calculate_kelly_fraction(self, win_rate: float, market_price: float) -> float:
        """
        Calculate Kelly Criterion optimal fraction
        
        Args:
            win_rate: Probability of winning (0-1)
            market_price: Current market price (0-1)
            
        Returns:
            Kelly optimal fraction (f*)
        """
        if not 0 < win_rate < 1:
            raise ValueError(f"Win rate must be between 0 and 1, got {win_rate}")
        if not 0 < market_price < 1:
            raise ValueError(f"Market price must be between 0 and 1, got {market_price}")
        
        # For binary markets, net odds b = (1/price) - 1
        # If we buy YES at price p, we pay p and get 1 if we win
        # Net odds = (1 - p) / p
        b = (1 / market_price) - 1
        
        # Kelly formula: f* = (p * b - q) / b
        # where p = win_rate, q = 1 - win_rate
        p = win_rate
        q = 1 - win_rate
        
        kelly_fraction = (p * b - q) / b
        
        # Kelly can be negative if edge is negative (don't bet)
        return max(0, kelly_fraction)
    
    def calculate_current_exposure(self, existing_positions: List[Position]) -> Tuple[float, float]:
        """
        Calculate current exposure from existing positions
        
        Args:
            existing_positions: List of current positions
            
        Returns:
            (total_exposure_usdc, total_exposure_pct)
        """
        total_exposure = sum(pos.size for pos in existing_positions)
        exposure_pct = (total_exposure / self.bankroll) * 100
        return total_exposure, exposure_pct
    
    def recommend_position_size(
        self,
        strategy: str,
        win_rate: float,
        market_price: float,
        existing_positions: List[Position],
        custom_kelly_fraction: Optional[float] = None
    ) -> PositionRecommendation:
        """
        Calculate recommended position size with risk management
        
        Args:
            strategy: Strategy name
            win_rate: Expected win rate for this strategy (0-1)
            market_price: Current market price (0-1)
            existing_positions: List of existing positions
            custom_kelly_fraction: Override default Quarter-Kelly (optional)
            
        Returns:
            PositionRecommendation with size and risk assessment
        """
        warnings = []
        
        # Calculate Kelly fraction
        full_kelly = self.calculate_kelly_fraction(win_rate, market_price)
        
        # Apply Kelly adjustment (default Quarter-Kelly)
        kelly_mult = custom_kelly_fraction or self.KELLY_FRACTION
        kelly_pct = full_kelly * kelly_mult * 100
        
        # Calculate current exposure
        current_exposure_usdc, current_exposure_pct = self.calculate_current_exposure(existing_positions)
        
        # Start with Kelly-suggested size
        recommended_pct = kelly_pct
        recommended_size = (recommended_pct / 100) * self.bankroll
        
        # Apply single position limit
        if recommended_pct > self.MAX_SINGLE_POSITION_PCT:
            warnings.append(
                f"Kelly suggests {recommended_pct:.2f}% but capped at {self.MAX_SINGLE_POSITION_PCT}% single position limit"
            )
            recommended_pct = self.MAX_SINGLE_POSITION_PCT
            recommended_size = (recommended_pct / 100) * self.bankroll
        
        # Check total exposure limit
        total_after_pct = current_exposure_pct + recommended_pct
        
        if total_after_pct > self.MAX_TOTAL_EXPOSURE_PCT:
            # Reduce position to stay within total exposure limit
            available_pct = self.MAX_TOTAL_EXPOSURE_PCT - current_exposure_pct
            
            if available_pct <= 0:
                warnings.append(
                    f"Already at max exposure ({current_exposure_pct:.2f}%). Cannot open new positions."
                )
                recommended_pct = 0
                recommended_size = 0
            else:
                warnings.append(
                    f"Reduced from {recommended_pct:.2f}% to {available_pct:.2f}% to stay within {self.MAX_TOTAL_EXPOSURE_PCT}% total exposure limit"
                )
                recommended_pct = available_pct
                recommended_size = (recommended_pct / 100) * self.bankroll
            
            total_after_pct = self.MAX_TOTAL_EXPOSURE_PCT
        
        # Edge case: no edge (Kelly suggests 0)
        if full_kelly <= 0:
            warnings.append(
                f"No positive edge detected (win rate: {win_rate:.1%}, price: {market_price:.3f}). Kelly suggests 0%."
            )
            recommended_pct = 0
            recommended_size = 0
        
        # Determine risk level
        risk_level = self._assess_risk_level(recommended_pct, total_after_pct)
        
        # Can trade if we have a positive size and not blocked
        can_trade = recommended_size > 0 and risk_level != RiskLevel.BLOCKED
        
        return PositionRecommendation(
            strategy=strategy,
            recommended_size_usdc=recommended_size,
            recommended_pct=recommended_pct,
            kelly_fraction=full_kelly,
            quarter_kelly_pct=kelly_pct,
            current_exposure_pct=current_exposure_pct,
            total_exposure_after_pct=total_after_pct,
            risk_level=risk_level,
            warnings=warnings,
            can_trade=can_trade
        )
    
    def _assess_risk_level(self, position_pct: float, total_exposure_pct: float) -> RiskLevel:
        """Assess risk level based on position size and total exposure"""
        
        # Blocked if exceeding limits
        if total_exposure_pct >= self.MAX_TOTAL_EXPOSURE_PCT:
            return RiskLevel.BLOCKED
        
        # Critical if close to limits
        if (position_pct >= self.MAX_SINGLE_POSITION_PCT * 0.9 or 
            total_exposure_pct >= self.MAX_TOTAL_EXPOSURE_PCT * 0.9):
            return RiskLevel.CRITICAL
        
        # Warning if over 50% of limits
        if (position_pct >= self.MAX_SINGLE_POSITION_PCT * 0.5 or
            total_exposure_pct >= self.MAX_TOTAL_EXPOSURE_PCT * 0.5):
            return RiskLevel.WARNING
        
        return RiskLevel.SAFE
    
    def batch_recommendations(
        self,
        opportunities: List[Tuple[str, float, float]],
        existing_positions: List[Position]
    ) -> List[PositionRecommendation]:
        """
        Get recommendations for multiple opportunities
        
        Args:
            opportunities: List of (strategy, win_rate, market_price) tuples
            existing_positions: Current positions
            
        Returns:
            List of recommendations sorted by recommended size
        """
        recommendations = []
        
        for strategy, win_rate, market_price in opportunities:
            rec = self.recommend_position_size(
                strategy=strategy,
                win_rate=win_rate,
                market_price=market_price,
                existing_positions=existing_positions
            )
            recommendations.append(rec)
        
        # Sort by recommended size (largest first)
        return sorted(recommendations, key=lambda r: r.recommended_size_usdc, reverse=True)


# ============================================================================
# EXAMPLE USAGE - 5 TRADING STRATEGIES
# ============================================================================

def example_usage():
    """
    Example usage with 5 different Polymarket trading strategies
    """
    
    print("\n" + "="*80)
    print("KELLY CRITERION POSITION SIZER - EXAMPLE USAGE")
    print("="*80)
    
    # Initialize with current bankroll
    BANKROLL = 10000  # $10,000 USDC
    sizer = PositionSizer(bankroll=BANKROLL)
    
    print(f"\n💰 Current Bankroll: ${BANKROLL:,.2f} USDC")
    print(f"📊 Risk Limits: {sizer.MAX_SINGLE_POSITION_PCT}% per position, {sizer.MAX_TOTAL_EXPOSURE_PCT}% total")
    
    # Existing positions
    existing_positions = [
        Position(market_id="market_001", size=500, strategy="High-Conviction Value"),
        Position(market_id="market_002", size=300, strategy="Momentum Reversal"),
    ]
    
    current_exposure = sum(p.size for p in existing_positions)
    print(f"💼 Current Exposure: ${current_exposure:,.2f} ({current_exposure/BANKROLL*100:.2f}%)")
    
    # ========================================================================
    # STRATEGY 1: High-Conviction Value Plays
    # ========================================================================
    print("\n" + "="*80)
    print("STRATEGY 1: High-Conviction Value Plays")
    print("="*80)
    print("Description: Markets with large edge, underpriced by >10%")
    print("Historical Win Rate: 68%")
    
    rec1 = sizer.recommend_position_size(
        strategy="High-Conviction Value",
        win_rate=0.68,
        market_price=0.45,  # Market at 45%, we think true prob is 68%
        existing_positions=existing_positions
    )
    print(rec1)
    
    # ========================================================================
    # STRATEGY 2: Momentum Reversal
    # ========================================================================
    print("="*80)
    print("STRATEGY 2: Momentum Reversal")
    print("="*80)
    print("Description: Fade extreme moves, mean reversion plays")
    print("Historical Win Rate: 58%")
    
    rec2 = sizer.recommend_position_size(
        strategy="Momentum Reversal",
        win_rate=0.58,
        market_price=0.72,  # Market overreacted to 72%, we think 58% is fair
        existing_positions=existing_positions
    )
    print(rec2)
    
    # ========================================================================
    # STRATEGY 3: Event Arbitrage
    # ========================================================================
    print("="*80)
    print("STRATEGY 3: Event Arbitrage")
    print("="*80)
    print("Description: Correlated markets with pricing discrepancies")
    print("Historical Win Rate: 75% (high conviction when edge exists)")
    
    rec3 = sizer.recommend_position_size(
        strategy="Event Arbitrage",
        win_rate=0.75,
        market_price=0.55,  # Strong edge
        existing_positions=existing_positions
    )
    print(rec3)
    
    # ========================================================================
    # STRATEGY 4: News Catalyst Plays
    # ========================================================================
    print("="*80)
    print("STRATEGY 4: News Catalyst Plays")
    print("="*80)
    print("Description: Fast-moving markets after news, information edge")
    print("Historical Win Rate: 62%")
    
    rec4 = sizer.recommend_position_size(
        strategy="News Catalyst",
        win_rate=0.62,
        market_price=0.48,
        existing_positions=existing_positions
    )
    print(rec4)
    
    # ========================================================================
    # STRATEGY 5: Low-Confidence Speculation
    # ========================================================================
    print("="*80)
    print("STRATEGY 5: Low-Confidence Speculation")
    print("="*80)
    print("Description: Weak edge, exploratory positions")
    print("Historical Win Rate: 53% (barely positive)")
    
    rec5 = sizer.recommend_position_size(
        strategy="Low-Confidence Spec",
        win_rate=0.53,
        market_price=0.48,  # Minimal edge
        existing_positions=existing_positions
    )
    print(rec5)
    
    # ========================================================================
    # BATCH COMPARISON
    # ========================================================================
    print("\n" + "="*80)
    print("BATCH COMPARISON - ALL OPPORTUNITIES")
    print("="*80)
    
    opportunities = [
        ("High-Conviction Value", 0.68, 0.45),
        ("Momentum Reversal", 0.58, 0.72),
        ("Event Arbitrage", 0.75, 0.55),
        ("News Catalyst", 0.62, 0.48),
        ("Low-Confidence Spec", 0.53, 0.48),
    ]
    
    recommendations = sizer.batch_recommendations(opportunities, existing_positions)
    
    print("\nRanked by recommended size:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.strategy:25s} → ${rec.recommended_size_usdc:8,.2f} ({rec.recommended_pct:5.2f}%) - {rec.risk_level.value}")
    
    # ========================================================================
    # EDGE CASE: No Edge (Don't Trade)
    # ========================================================================
    print("\n" + "="*80)
    print("EDGE CASE: No Positive Edge")
    print("="*80)
    
    rec_no_edge = sizer.recommend_position_size(
        strategy="No Edge Example",
        win_rate=0.45,
        market_price=0.48,  # Market is BETTER than our estimate - no edge!
        existing_positions=existing_positions
    )
    print(rec_no_edge)
    
    # ========================================================================
    # EDGE CASE: Already at max exposure
    # ========================================================================
    print("="*80)
    print("EDGE CASE: Already at Max Exposure")
    print("="*80)
    
    # Simulate being at max exposure
    max_exposure_positions = [
        Position(market_id=f"market_{i}", size=500, strategy="Various")
        for i in range(5)
    ]  # 5 x $500 = $2,500 = 25% of $10k
    
    rec_maxed = sizer.recommend_position_size(
        strategy="Blocked by Exposure",
        win_rate=0.70,
        market_price=0.45,
        existing_positions=max_exposure_positions
    )
    print(rec_maxed)


if __name__ == "__main__":
    example_usage()
