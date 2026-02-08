#!/usr/bin/env python3
"""
Portfolio Optimizer for Polymarket Trading System

A multi-market portfolio optimization module implementing Kelly Criterion,
correlation analysis, sector exposure limits, and comprehensive risk metrics.

Author: OpenClaw Agent
License: MIT
"""

import argparse
import json
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Try to use numpy for better performance, fallback to pure Python
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Warning: numpy not available, using pure Python (slower)", file=sys.stderr)


class Sector(Enum):
    """Market sectors for exposure limits"""
    CRYPTO = "crypto"
    POLITICS = "politics"
    SPORTS = "sports"
    OTHER = "other"


# Sector exposure limits (as decimal)
SECTOR_LIMITS = {
    Sector.CRYPTO: 0.30,
    Sector.POLITICS: 0.30,
    Sector.SPORTS: 0.20,
    Sector.OTHER: 0.20,
}


@dataclass
class Position:
    """Represents a position in a prediction market"""
    market_id: str
    amount: float  # Current position size
    probability: float  # Your estimated probability of winning (0-1)
    market_price: float  # Current market price (0-1)
    sector: Sector
    historical_returns: List[float] = None  # For calculating Sharpe/Sortino
    
    def __post_init__(self):
        if self.historical_returns is None:
            self.historical_returns = []
    
    @property
    def edge(self) -> float:
        """Calculate edge: difference between your probability and market price"""
        return self.probability - self.market_price
    
    @property
    def expected_value(self) -> float:
        """Expected value of this position"""
        # EV = P(win) * (1/price - 1) - P(lose)
        # Simplified: EV = probability - market_price
        return self.edge


class PortfolioOptimizer:
    """
    Multi-market portfolio optimizer using Kelly Criterion with correlation adjustment.
    
    Features:
    - Fractional Kelly (25% for safety)
    - Correlation matrix for correlated bets
    - Sector exposure limits
    - Dynamic rebalancing suggestions
    - Comprehensive risk metrics
    """
    
    def __init__(self, bankroll: float, fractional_kelly: float = 0.25):
        """
        Initialize portfolio optimizer.
        
        Args:
            bankroll: Total bankroll in dollars
            fractional_kelly: Fraction of Kelly to use (default 0.25 for safety)
        """
        self.bankroll = bankroll
        self.fractional_kelly = fractional_kelly
        self.positions: Dict[str, Position] = {}
        self.correlation_matrix: Dict[Tuple[str, str], float] = {}
        
    def add_position(self, market_id: str, amount: float, probability: float, 
                    market_price: float = None, sector: Sector = Sector.OTHER,
                    historical_returns: List[float] = None) -> None:
        """
        Add or update a position.
        
        Args:
            market_id: Unique market identifier
            amount: Current position size in dollars
            probability: Your estimated probability of winning (0-1)
            market_price: Current market price (0-1), defaults to probability
            sector: Market sector for exposure limits
            historical_returns: List of historical returns for risk metrics
        """
        if market_price is None:
            market_price = probability
            
        self.positions[market_id] = Position(
            market_id=market_id,
            amount=amount,
            probability=probability,
            market_price=market_price,
            sector=sector,
            historical_returns=historical_returns or []
        )
    
    def set_correlation(self, market_id_1: str, market_id_2: str, correlation: float) -> None:
        """
        Set correlation between two markets.
        
        Args:
            market_id_1: First market ID
            market_id_2: Second market ID
            correlation: Correlation coefficient (-1 to 1)
        """
        # Store both directions for easy lookup
        self.correlation_matrix[(market_id_1, market_id_2)] = correlation
        self.correlation_matrix[(market_id_2, market_id_1)] = correlation
    
    def get_correlation(self, market_id_1: str, market_id_2: str) -> float:
        """Get correlation between two markets (0 if not set)"""
        return self.correlation_matrix.get((market_id_1, market_id_2), 0.0)
    
    def calculate_kelly_fraction(self, position: Position) -> float:
        """
        Calculate Kelly Criterion fraction for a single position.
        
        Kelly formula: f = (p * b - q) / b
        where:
        - p = probability of winning
        - q = probability of losing (1 - p)
        - b = odds (1/market_price - 1)
        
        For prediction markets:
        - If you buy at price P and win, you get 1/P
        - Net odds: b = (1/P - 1)
        
        Simplified Kelly for prediction markets:
        f = (p - P) / (1 - P) where P is market price
        
        Args:
            position: Position object
            
        Returns:
            Kelly fraction (0-1)
        """
        p = position.probability
        P = position.market_price
        
        # Edge must be positive for Kelly
        if p <= P:
            return 0.0
        
        # Kelly formula for prediction markets
        # f = (p - P) / (1 - P)
        if P >= 1.0:
            return 0.0
            
        kelly_fraction = (p - P) / (1 - P)
        
        # Cap at 1 (never bet more than 100% of bankroll)
        return min(max(kelly_fraction, 0.0), 1.0)
    
    def calculate_optimal_allocation(self) -> Dict[str, float]:
        """
        Calculate optimal allocation across all positions using Kelly Criterion
        with correlation adjustments.
        
        For correlated bets, we reduce Kelly fractions:
        - High correlation (>0.7): reduce by 50%
        - Medium correlation (0.4-0.7): reduce by 30%
        - Low correlation (<0.4): reduce by 10%
        
        Returns:
            Dict mapping market_id to suggested dollar amount
        """
        allocations = {}
        
        for market_id, position in self.positions.items():
            # Calculate base Kelly fraction
            kelly_frac = self.calculate_kelly_fraction(position)
            
            # Apply fractional Kelly (e.g., 25% Kelly for safety)
            adjusted_kelly = kelly_frac * self.fractional_kelly
            
            # Check correlation with other positions
            correlation_penalty = 0.0
            for other_id, other_pos in self.positions.items():
                if other_id == market_id:
                    continue
                    
                corr = abs(self.get_correlation(market_id, other_id))
                
                # Apply correlation penalty
                if corr > 0.7:
                    correlation_penalty = max(correlation_penalty, 0.5)
                elif corr > 0.4:
                    correlation_penalty = max(correlation_penalty, 0.3)
                elif corr > 0.1:
                    correlation_penalty = max(correlation_penalty, 0.1)
            
            # Reduce allocation based on correlation
            final_kelly = adjusted_kelly * (1 - correlation_penalty)
            
            # Calculate dollar allocation
            allocations[market_id] = final_kelly * self.bankroll
        
        # Apply sector limits
        allocations = self._apply_sector_limits(allocations)
        
        return allocations
    
    def _apply_sector_limits(self, allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Apply sector exposure limits to allocations.
        
        If a sector exceeds its limit, proportionally reduce all positions
        in that sector.
        
        Args:
            allocations: Initial allocations
            
        Returns:
            Adjusted allocations respecting sector limits
        """
        # Calculate sector exposures
        sector_exposure = {sector: 0.0 for sector in Sector}
        
        for market_id, amount in allocations.items():
            position = self.positions[market_id]
            sector_exposure[position.sector] += amount
        
        # Check and adjust sectors exceeding limits
        adjusted = allocations.copy()
        
        for sector, total_exposure in sector_exposure.items():
            limit = SECTOR_LIMITS[sector] * self.bankroll
            
            if total_exposure > limit:
                # Calculate reduction factor
                reduction_factor = limit / total_exposure
                
                # Apply reduction to all positions in this sector
                for market_id in allocations:
                    if self.positions[market_id].sector == sector:
                        adjusted[market_id] *= reduction_factor
        
        return adjusted
    
    def calculate_rebalance_orders(self, target_drift_threshold: float = 0.05) -> Dict[str, float]:
        """
        Generate rebalancing orders when positions drift from optimal.
        
        Args:
            target_drift_threshold: Rebalance if position drifts >5% from optimal
            
        Returns:
            Dict mapping market_id to rebalance amount (positive = buy, negative = sell)
        """
        optimal = self.calculate_optimal_allocation()
        orders = {}
        
        for market_id, optimal_amount in optimal.items():
            current_amount = self.positions[market_id].amount
            drift = abs(optimal_amount - current_amount) / self.bankroll
            
            if drift > target_drift_threshold:
                orders[market_id] = optimal_amount - current_amount
        
        # Prioritize orders: sell first (risk reduction), then buy
        sell_orders = {k: v for k, v in orders.items() if v < 0}
        buy_orders = {k: v for k, v in orders.items() if v > 0}
        
        # Sort sells by magnitude (largest sells first for liquidity)
        sorted_sells = dict(sorted(sell_orders.items(), key=lambda x: x[1]))
        # Sort buys by edge (best opportunities first)
        sorted_buys = dict(sorted(
            buy_orders.items(), 
            key=lambda x: self.positions[x[0]].edge,
            reverse=True
        ))
        
        # Combine: sells first, then buys
        return {**sorted_sells, **sorted_buys}
    
    def calculate_sharpe_ratio(self, market_id: str, risk_free_rate: float = 0.0) -> Optional[float]:
        """
        Calculate Sharpe ratio for a position.
        
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        
        Args:
            market_id: Market identifier
            risk_free_rate: Annual risk-free rate (default 0)
            
        Returns:
            Sharpe ratio or None if insufficient data
        """
        position = self.positions.get(market_id)
        if not position or len(position.historical_returns) < 2:
            return None
        
        returns = position.historical_returns
        
        if HAS_NUMPY:
            mean_return = np.mean(returns)
            std_return = np.std(returns, ddof=1)
        else:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
            std_return = variance ** 0.5
        
        if std_return == 0:
            return None
            
        return (mean_return - risk_free_rate) / std_return
    
    def calculate_sortino_ratio(self, market_id: str, risk_free_rate: float = 0.0) -> Optional[float]:
        """
        Calculate Sortino ratio (penalizes only downside volatility).
        
        Sortino = (Mean Return - Risk Free Rate) / Downside Deviation
        
        Args:
            market_id: Market identifier
            risk_free_rate: Annual risk-free rate (default 0)
            
        Returns:
            Sortino ratio or None if insufficient data
        """
        position = self.positions.get(market_id)
        if not position or len(position.historical_returns) < 2:
            return None
        
        returns = position.historical_returns
        
        if HAS_NUMPY:
            mean_return = np.mean(returns)
            # Only consider negative returns for downside deviation
            downside_returns = [r for r in returns if r < risk_free_rate]
        else:
            mean_return = sum(returns) / len(returns)
            downside_returns = [r for r in returns if r < risk_free_rate]
        
        if len(downside_returns) < 2:
            return None
        
        if HAS_NUMPY:
            downside_dev = np.std(downside_returns, ddof=1)
        else:
            mean_downside = sum(downside_returns) / len(downside_returns)
            variance = sum((r - mean_downside) ** 2 for r in downside_returns) / (len(downside_returns) - 1)
            downside_dev = variance ** 0.5
        
        if downside_dev == 0:
            return None
            
        return (mean_return - risk_free_rate) / downside_dev
    
    def calculate_max_drawdown(self, market_id: str) -> Optional[float]:
        """
        Calculate maximum drawdown from peak for a position.
        
        Args:
            market_id: Market identifier
            
        Returns:
            Maximum drawdown as a fraction (e.g., -0.25 for 25% drawdown)
        """
        position = self.positions.get(market_id)
        if not position or len(position.historical_returns) < 2:
            return None
        
        returns = position.historical_returns
        
        # Calculate cumulative returns
        cumulative = [1.0]
        for r in returns:
            cumulative.append(cumulative[-1] * (1 + r))
        
        max_drawdown = 0.0
        peak = cumulative[0]
        
        for value in cumulative:
            if value > peak:
                peak = value
            drawdown = (value - peak) / peak
            if drawdown < max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def calculate_hhi(self) -> float:
        """
        Calculate Herfindahl-Hirschman Index (HHI) for concentration risk.
        
        HHI = sum of squared market shares
        - HHI < 0.15: Low concentration
        - 0.15 < HHI < 0.25: Moderate concentration
        - HHI > 0.25: High concentration
        
        Returns:
            HHI value
        """
        total_exposure = sum(pos.amount for pos in self.positions.values())
        
        if total_exposure == 0:
            return 0.0
        
        hhi = sum((pos.amount / total_exposure) ** 2 for pos in self.positions.values())
        return hhi
    
    def calculate_var(self, confidence_level: float = 0.95) -> float:
        """
        Calculate portfolio Value at Risk (VaR) using historical simulation.
        
        VaR estimates the maximum loss at a given confidence level.
        
        Args:
            confidence_level: Confidence level (default 0.95 for 95% VaR)
            
        Returns:
            VaR as a dollar amount (positive number represents potential loss)
        """
        # Collect all historical returns across positions
        all_returns = []
        for position in self.positions.values():
            if position.historical_returns:
                all_returns.extend(position.historical_returns)
        
        if not all_returns:
            return 0.0
        
        # Sort returns
        all_returns.sort()
        
        # Find the percentile corresponding to the confidence level
        # VaR is the loss at the (1 - confidence_level) percentile
        index = int(len(all_returns) * (1 - confidence_level))
        
        if index >= len(all_returns):
            index = len(all_returns) - 1
        
        var_return = all_returns[index]
        
        # Convert to dollar amount
        total_exposure = sum(pos.amount for pos in self.positions.values())
        var_dollars = abs(var_return * total_exposure)
        
        return var_dollars
    
    def analyze_portfolio(self) -> Dict:
        """
        Comprehensive portfolio analysis.
        
        Returns:
            Dict containing all portfolio metrics
        """
        total_exposure = sum(pos.amount for pos in self.positions.values())
        
        # Sector breakdown
        sector_breakdown = {sector.value: 0.0 for sector in Sector}
        for position in self.positions.values():
            sector_breakdown[position.sector.value] += position.amount
        
        # Expected return
        expected_return = sum(pos.amount * pos.expected_value for pos in self.positions.values())
        
        # Calculate metrics
        hhi = self.calculate_hhi()
        var_95 = self.calculate_var(0.95)
        
        # Risk concentration warnings
        warnings = []
        
        # Check sector limits
        for sector, amount in sector_breakdown.items():
            limit = SECTOR_LIMITS[Sector(sector)] * self.bankroll
            if amount > limit:
                pct = (amount / self.bankroll) * 100
                limit_pct = (limit / self.bankroll) * 100
                warnings.append(f"⚠️  {sector.upper()} exposure ({pct:.1f}%) exceeds limit ({limit_pct:.1f}%)")
        
        # Check HHI
        if hhi > 0.25:
            warnings.append(f"⚠️  High concentration risk (HHI={hhi:.3f})")
        
        # Check correlations
        high_correlations = []
        checked_pairs = set()
        for m1 in self.positions:
            for m2 in self.positions:
                if m1 >= m2:
                    continue
                pair = tuple(sorted([m1, m2]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                
                corr = abs(self.get_correlation(m1, m2))
                if corr > 0.7:
                    high_correlations.append((m1, m2, corr))
        
        if high_correlations:
            warnings.append(f"⚠️  {len(high_correlations)} highly correlated position pairs (>0.7)")
        
        return {
            "total_exposure": total_exposure,
            "bankroll": self.bankroll,
            "utilization": total_exposure / self.bankroll if self.bankroll > 0 else 0,
            "sector_breakdown": sector_breakdown,
            "expected_return": expected_return,
            "hhi": hhi,
            "var_95": var_95,
            "num_positions": len(self.positions),
            "warnings": warnings,
            "high_correlations": high_correlations,
        }
    
    def calculate_risk_metrics(self) -> Dict:
        """
        Calculate risk metrics for all positions.
        
        Returns:
            Dict mapping market_id to risk metrics
        """
        metrics = {}
        
        for market_id in self.positions:
            sharpe = self.calculate_sharpe_ratio(market_id)
            sortino = self.calculate_sortino_ratio(market_id)
            max_dd = self.calculate_max_drawdown(market_id)
            
            metrics[market_id] = {
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "max_drawdown": max_dd,
                "edge": self.positions[market_id].edge,
                "expected_value": self.positions[market_id].expected_value,
            }
        
        return metrics
    
    def optimize(self) -> Dict:
        """
        Run full optimization and return recommendations.
        
        Returns:
            Dict containing optimal allocations and analysis
        """
        allocations = self.calculate_optimal_allocation()
        analysis = self.analyze_portfolio()
        
        return {
            "optimal_allocations": allocations,
            "current_analysis": analysis,
        }
    
    def print_analysis(self) -> None:
        """Print formatted portfolio analysis to console"""
        analysis = self.analyze_portfolio()
        
        print("\n" + "="*60)
        print("📊 PORTFOLIO ANALYSIS")
        print("="*60)
        
        print(f"\n💰 Total Exposure: ${analysis['total_exposure']:,.2f}")
        print(f"💵 Bankroll: ${analysis['bankroll']:,.2f}")
        print(f"📈 Utilization: {analysis['utilization']*100:.1f}%")
        print(f"💸 Expected Return: ${analysis['expected_return']:,.2f}")
        
        print(f"\n🎯 Sector Breakdown:")
        for sector, amount in analysis['sector_breakdown'].items():
            pct = (amount / self.bankroll * 100) if self.bankroll > 0 else 0
            limit_pct = SECTOR_LIMITS[Sector(sector)] * 100
            print(f"  {sector.upper():12s}: ${amount:8,.2f} ({pct:5.1f}%) [limit: {limit_pct:.0f}%]")
        
        print(f"\n⚠️  Risk Metrics:")
        print(f"  HHI (concentration): {analysis['hhi']:.3f}")
        if analysis['hhi'] < 0.15:
            print(f"    → Low concentration ✓")
        elif analysis['hhi'] < 0.25:
            print(f"    → Moderate concentration")
        else:
            print(f"    → High concentration risk!")
        
        print(f"  VaR (95%): ${analysis['var_95']:,.2f}")
        print(f"  Positions: {analysis['num_positions']}")
        
        if analysis['warnings']:
            print(f"\n🚨 Warnings:")
            for warning in analysis['warnings']:
                print(f"  {warning}")
        
        if analysis['high_correlations']:
            print(f"\n🔗 High Correlations:")
            for m1, m2, corr in analysis['high_correlations'][:5]:  # Show top 5
                print(f"  {m1} ↔ {m2}: {corr:.3f}")
    
    def print_optimization(self) -> None:
        """Print formatted optimization results"""
        allocations = self.calculate_optimal_allocation()
        
        print("\n" + "="*60)
        print("🎯 OPTIMAL ALLOCATION (Kelly Criterion)")
        print("="*60)
        
        print(f"\nFractional Kelly: {self.fractional_kelly*100:.0f}%")
        print(f"Bankroll: ${self.bankroll:,.2f}\n")
        
        # Sort by allocation amount
        sorted_allocs = sorted(allocations.items(), key=lambda x: x[1], reverse=True)
        
        for market_id, amount in sorted_allocs:
            position = self.positions[market_id]
            current = position.amount
            change = amount - current
            pct = (amount / self.bankroll * 100) if self.bankroll > 0 else 0
            
            change_str = f"({change:+,.2f})" if change != 0 else ""
            
            print(f"{market_id:20s} ${amount:8,.2f} ({pct:5.1f}%) {change_str}")
            print(f"  Current: ${current:,.2f} | Edge: {position.edge:+.3f} | "
                  f"Prob: {position.probability:.2f} | Price: {position.market_price:.2f}")
    
    def print_rebalance(self) -> None:
        """Print formatted rebalancing orders"""
        orders = self.calculate_rebalance_orders()
        
        if not orders:
            print("\n✓ Portfolio is balanced (drift <5%)")
            return
        
        print("\n" + "="*60)
        print("🔄 REBALANCING ORDERS")
        print("="*60)
        
        sell_orders = {k: v for k, v in orders.items() if v < 0}
        buy_orders = {k: v for k, v in orders.items() if v > 0}
        
        if sell_orders:
            print("\n📉 SELL (Risk Reduction):")
            for market_id, amount in sell_orders.items():
                print(f"  {market_id:20s} ${abs(amount):,.2f}")
        
        if buy_orders:
            print("\n📈 BUY (New Positions):")
            for market_id, amount in buy_orders.items():
                position = self.positions[market_id]
                print(f"  {market_id:20s} ${amount:,.2f} (edge: {position.edge:+.3f})")
    
    def print_risk_metrics(self) -> None:
        """Print formatted risk metrics for all positions"""
        metrics = self.calculate_risk_metrics()
        
        print("\n" + "="*60)
        print("📊 RISK METRICS BY POSITION")
        print("="*60)
        
        for market_id, m in metrics.items():
            print(f"\n{market_id}:")
            print(f"  Edge: {m['edge']:+.3f}")
            print(f"  Expected Value: ${m['expected_value']:+,.4f}")
            
            if m['sharpe_ratio'] is not None:
                print(f"  Sharpe Ratio: {m['sharpe_ratio']:.3f}")
            if m['sortino_ratio'] is not None:
                print(f"  Sortino Ratio: {m['sortino_ratio']:.3f}")
            if m['max_drawdown'] is not None:
                print(f"  Max Drawdown: {m['max_drawdown']*100:.1f}%")


def create_example_portfolio() -> PortfolioOptimizer:
    """Create example portfolio with 5 hypothetical markets"""
    
    print("\n" + "="*60)
    print("🎲 EXAMPLE: 5 Hypothetical Polymarket Positions")
    print("="*60)
    
    optimizer = PortfolioOptimizer(bankroll=10000, fractional_kelly=0.25)
    
    # Market 1: Bitcoin > $100k by EOY (Crypto)
    optimizer.add_position(
        market_id="btc_100k_eoy",
        amount=1500,
        probability=0.65,
        market_price=0.55,
        sector=Sector.CRYPTO,
        historical_returns=[0.15, -0.08, 0.22, 0.10, -0.05, 0.18, 0.12]
    )
    
    # Market 2: Ethereum > $5k by Q2 (Crypto - correlated with BTC)
    optimizer.add_position(
        market_id="eth_5k_q2",
        amount=1200,
        probability=0.58,
        market_price=0.50,
        sector=Sector.CRYPTO,
        historical_returns=[0.12, -0.10, 0.25, 0.08, -0.06, 0.20, 0.14]
    )
    
    # Market 3: Democrat wins 2024 (Politics)
    optimizer.add_position(
        market_id="dem_win_2024",
        amount=2000,
        probability=0.52,
        market_price=0.48,
        sector=Sector.POLITICS,
        historical_returns=[0.05, 0.02, -0.03, 0.04, 0.01, -0.02, 0.03]
    )
    
    # Market 4: Lakers win NBA championship (Sports)
    optimizer.add_position(
        market_id="lakers_champion",
        amount=800,
        probability=0.25,
        market_price=0.15,
        sector=Sector.SPORTS,
        historical_returns=[0.30, -0.15, -0.10, 0.40, -0.20, 0.25]
    )
    
    # Market 5: AI reaches AGI in 2025 (Other)
    optimizer.add_position(
        market_id="agi_2025",
        amount=500,
        probability=0.15,
        market_price=0.20,
        sector=Sector.OTHER,
        historical_returns=[0.10, 0.05, -0.12, 0.08, -0.08, 0.15]
    )
    
    # Set correlations
    # BTC and ETH are highly correlated
    optimizer.set_correlation("btc_100k_eoy", "eth_5k_q2", 0.85)
    
    # Politics and crypto have weak correlation
    optimizer.set_correlation("btc_100k_eoy", "dem_win_2024", 0.15)
    optimizer.set_correlation("eth_5k_q2", "dem_win_2024", 0.12)
    
    print("\n✓ Created 5 positions across 4 sectors")
    print("✓ Set correlation between BTC and ETH (0.85)")
    
    return optimizer


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Portfolio Optimizer for Polymarket Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python portfolio-optimizer.py --analyze          # Analyze current portfolio
  python portfolio-optimizer.py --optimize         # Suggest optimal allocation
  python portfolio-optimizer.py --rebalance        # Generate rebalance orders
  python portfolio-optimizer.py --risk             # Risk metrics
  python portfolio-optimizer.py --example          # Run example with 5 markets
        """
    )
    
    parser.add_argument("--analyze", action="store_true", 
                       help="Analyze current portfolio")
    parser.add_argument("--optimize", action="store_true",
                       help="Calculate optimal allocation using Kelly Criterion")
    parser.add_argument("--rebalance", action="store_true",
                       help="Generate rebalancing orders")
    parser.add_argument("--risk", action="store_true",
                       help="Show risk metrics for all positions")
    parser.add_argument("--example", action="store_true",
                       help="Run example with 5 hypothetical markets")
    parser.add_argument("--all", action="store_true",
                       help="Run all analyses")
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any([args.analyze, args.optimize, args.rebalance, args.risk, args.example, args.all]):
        parser.print_help()
        return
    
    # Create example portfolio
    optimizer = create_example_portfolio()
    
    # Run requested analyses
    if args.example or args.analyze or args.all:
        optimizer.print_analysis()
    
    if args.example or args.optimize or args.all:
        optimizer.print_optimization()
    
    if args.example or args.rebalance or args.all:
        optimizer.print_rebalance()
    
    if args.example or args.risk or args.all:
        optimizer.print_risk_metrics()


if __name__ == "__main__":
    main()
