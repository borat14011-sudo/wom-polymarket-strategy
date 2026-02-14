"""
Risk Manager for Polymarket Trading Bot
Handles position sizing, exposure checks, and risk limits
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math

@dataclass
class RiskParameters:
    """Risk management parameters"""
    max_position_size: float = 0.20  # $0.20 per trade
    max_total_exposure: float = 2.50  # $2.50 total exposure
    max_concurrent_positions: int = 3  # Max 3 positions at once
    stop_loss_pct: float = 12.0  # 12% stop loss
    circuit_breaker_pct: float = 15.0  # 15% drawdown circuit breaker
    kelly_fraction: float = 0.25  # Use 25% of Kelly criterion
    min_expected_value: float = 0.03  # Minimum 3% expected value

@dataclass
class Position:
    """Represents a position for risk calculation"""
    token_id: str
    side: str  # "YES" or "NO"
    price: float
    size: float
    cost: float

class RiskManager:
    """Manages trading risk and position sizing"""
    
    def __init__(self, risk_params: Optional[RiskParameters] = None):
        self.params = risk_params or RiskParameters()
        self.total_capital = 10.00  # Starting capital
    
    def can_trade(self, current_positions: List[Position], 
                  proposed_trade_cost: float) -> Tuple[bool, str]:
        """
        Check if a new trade is allowed given current positions
        
        Args:
            current_positions: List of current positions
            proposed_trade_cost: Cost of proposed trade
            
        Returns:
            Tuple of (allowed, reason)
        """
        # Check max position size
        if proposed_trade_cost > self.params.max_position_size:
            return False, f"Trade cost ${proposed_trade_cost:.4f} exceeds max position size ${self.params.max_position_size}"
        
        # Check max concurrent positions
        if len(current_positions) >= self.params.max_concurrent_positions:
            return False, f"Already have {len(current_positions)} positions, max is {self.params.max_concurrent_positions}"
        
        # Calculate total exposure
        total_exposure = sum(pos.cost for pos in current_positions)
        total_exposure += proposed_trade_cost
        
        if total_exposure > self.params.max_total_exposure:
            return False, f"Total exposure ${total_exposure:.4f} exceeds max ${self.params.max_total_exposure}"
        
        # Check if we have enough capital
        if total_exposure > self.total_capital:
            return False, f"Total exposure ${total_exposure:.4f} exceeds capital ${self.total_capital}"
        
        return True, "Trade allowed"
    
    def calculate_kelly_size(self, probability: float, odds: float, 
                            bankroll: float) -> float:
        """
        Calculate position size using Kelly Criterion
        
        Args:
            probability: Your estimated probability of winning (0 to 1)
            odds: Decimal odds (e.g., 1.5 for 50% market price)
            bankroll: Total available capital
            
        Returns:
            Fraction of bankroll to bet
        """
        if probability <= 0 or probability >= 1:
            return 0.0
        
        if odds <= 1.0:
            return 0.0
        
        # Kelly formula: f* = (bp - q) / b
        # where b = odds - 1, p = probability, q = 1 - p
        b = odds - 1
        p = probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Apply safety fraction
        safe_fraction = kelly_fraction * self.params.kelly_fraction
        
        # Ensure non-negative
        safe_fraction = max(0.0, safe_fraction)
        
        # Calculate dollar amount
        dollar_amount = safe_fraction * bankroll
        
        # Cap at max position size
        dollar_amount = min(dollar_amount, self.params.max_position_size)
        
        return dollar_amount
    
    def calculate_position_size(self, market_price: float, 
                               estimated_probability: float,
                               bankroll: float) -> float:
        """
        Calculate position size for a trade
        
        Args:
            market_price: Current market price (0 to 1)
            estimated_probability: Your estimated true probability (0 to 1)
            bankroll: Available capital
            
        Returns:
            Position size in dollars
        """
        # Skip if no edge
        if estimated_probability <= market_price:
            return 0.0
        
        # Calculate expected value
        expected_value = estimated_probability - market_price
        
        if expected_value < self.params.min_expected_value:
            return 0.0
        
        # Calculate decimal odds
        # If buying YES at price p, odds = 1/p
        # If buying NO at price p, odds = 1/(1-p)
        # We'll use the appropriate odds based on which side has edge
        
        if estimated_probability > market_price:
            # Buying YES has edge
            odds = 1.0 / market_price
            probability = estimated_probability
        else:
            # Buying NO has edge (estimated_probability refers to YES probability)
            # NO probability = 1 - estimated_probability
            # NO price = 1 - market_price
            odds = 1.0 / (1 - market_price)
            probability = 1 - estimated_probability
        
        # Calculate Kelly size
        kelly_size = self.calculate_kelly_size(probability, odds, bankroll)
        
        # Round to nearest cent
        kelly_size = round(kelly_size, 2)
        
        return kelly_size
    
    def check_circuit_breaker(self, starting_capital: float, 
                             current_capital: float) -> Tuple[bool, str]:
        """
        Check if circuit breaker should be triggered
        
        Args:
            starting_capital: Capital at start of trading period
            current_capital: Current capital
            
        Returns:
            Tuple of (triggered, reason)
        """
        if starting_capital <= 0:
            return False, "Starting capital must be positive"
        
        drawdown_pct = ((starting_capital - current_capital) / starting_capital) * 100
        
        if drawdown_pct >= self.params.circuit_breaker_pct:
            return True, f"Drawdown {drawdown_pct:.1f}% exceeds circuit breaker {self.params.circuit_breaker_pct}%"
        
        return False, f"Drawdown {drawdown_pct:.1f}% within limits"
    
    def calculate_stop_loss_price(self, entry_price: float, side: str) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price (0 to 1)
            side: "YES" or "NO"
            
        Returns:
            Stop loss price
        """
        if side.upper() == "YES":
            # For YES positions, stop loss triggers if price drops
            stop_loss_price = entry_price * (1 - self.params.stop_loss_pct / 100)
            return max(0.01, stop_loss_price)  # Don't go below 1 cent
        else:
            # For NO positions, stop loss triggers if price rises
            # NO price = 1 - YES price
            yes_price = 1 - entry_price
            stop_loss_yes_price = yes_price * (1 - self.params.stop_loss_pct / 100)
            stop_loss_no_price = 1 - stop_loss_yes_price
            return min(0.99, stop_loss_no_price)  # Don't go above 99 cents
    
    def calculate_expected_value(self, market_price: float, 
                                estimated_probability: float, 
                                trade_cost: float) -> Dict[str, float]:
        """
        Calculate expected value metrics
        
        Args:
            market_price: Current market price
            estimated_probability: Estimated true probability
            trade_cost: Cost of the trade
            
        Returns:
            Dictionary of EV metrics
        """
        # For YES position
        if estimated_probability > market_price:
            potential_profit = 1.0 - market_price  # If YES resolves to $1
            potential_loss = market_price  # If YES resolves to $0
            ev = (estimated_probability * potential_profit) - ((1 - estimated_probability) * potential_loss)
            ev_percent = (ev / market_price) * 100
            ev_dollars = ev * trade_cost / market_price  # Convert to dollar terms
        else:
            # For NO position
            no_market_price = 1 - market_price
            no_probability = 1 - estimated_probability
            potential_profit = 1.0 - no_market_price  # If NO resolves to $1
            potential_loss = no_market_price  # If NO resolves to $0
            ev = (no_probability * potential_profit) - ((1 - no_probability) * potential_loss)
            ev_percent = (ev / no_market_price) * 100
            ev_dollars = ev * trade_cost / no_market_price
        
        return {
            'expected_value': ev,
            'expected_value_percent': ev_percent,
            'expected_value_dollars': ev_dollars,
            'edge_percentage': abs(estimated_probability - market_price) * 100
        }
    
    def get_risk_report(self, positions: List[Position], 
                       bankroll: float, starting_capital: float) -> Dict:
        """
        Generate a risk report
        
        Args:
            positions: Current positions
            bankroll: Current capital
            starting_capital: Starting capital
            
        Returns:
            Risk report dictionary
        """
        total_exposure = sum(pos.cost for pos in positions)
        exposure_pct = (total_exposure / bankroll) * 100 if bankroll > 0 else 0
        
        circuit_breaker_triggered, circuit_reason = self.check_circuit_breaker(
            starting_capital, bankroll
        )
        
        # Calculate concentration risk
        concentration_risk = 0.0
        if total_exposure > 0:
            for pos in positions:
                position_pct = (pos.cost / total_exposure) * 100
                concentration_risk += position_pct ** 2  # Herfindahl index
        
        return {
            'total_positions': len(positions),
            'total_exposure': total_exposure,
            'exposure_percentage': exposure_pct,
            'remaining_capital': bankroll - total_exposure,
            'circuit_breaker_triggered': circuit_breaker_triggered,
            'circuit_breaker_reason': circuit_reason,
            'concentration_risk': concentration_risk,
            'max_position_size': self.params.max_position_size,
            'max_total_exposure': self.params.max_total_exposure,
            'max_concurrent_positions': self.params.max_concurrent_positions,
            'risk_limits_respected': (
                total_exposure <= self.params.max_total_exposure and
                len(positions) <= self.params.max_concurrent_positions and
                all(pos.cost <= self.params.max_position_size for pos in positions)
            )
        }
    
    def print_risk_report(self, positions: List[Position], 
                         bankroll: float, starting_capital: float):
        """Print formatted risk report"""
        report = self.get_risk_report(positions, bankroll, starting_capital)
        
        print("\n" + "="*60)
        print("RISK MANAGEMENT REPORT")
        print("="*60)
        
        print(f"\nPositions: {report['total_positions']}")
        print(f"Total Exposure: ${report['total_exposure']:.4f} ({report['exposure_percentage']:.1f}% of capital)")
        print(f"Remaining Capital: ${report['remaining_capital']:.4f}")
        
        print(f"\nRisk Limits:")
        print(f"  Max Position Size: ${report['max_position_size']}")
        print(f"  Max Total Exposure: ${report['max_total_exposure']}")
        print(f"  Max Concurrent Positions: {report['max_concurrent_positions']}")
        
        if report['circuit_breaker_triggered']:
            print(f"\n🚨 CIRCUIT BREAKER: {report['circuit_breaker_reason']}")
        else:
            print(f"\nCircuit Breaker: OK ({report['circuit_breaker_reason']})")
        
        if report['risk_limits_respected']:
            print("\n✅ All risk limits respected")
        else:
            print("\n⚠️  Risk limits exceeded!")
        
        print(f"\nConcentration Risk Score: {report['concentration_risk']:.2f}")
        if report['concentration_risk'] > 2500:  # > 50% in one position
            print("  ⚠️  High concentration risk detected")

if __name__ == "__main__":
    # Test the risk manager
    risk_mgr = RiskManager()
    
    # Test positions
    test_positions = [
        Position(
            token_id="token1",
            side="YES",
            price=0.15,
            size=1.33,  # $0.20
            cost=0.1995
        ),
        Position(
            token_id="token2", 
            side="NO",
            price=0.85,  # NO price = 1 - 0.85 = 0.15
            size=1.33,   # $0.20
            cost=0.1995
        )
    ]
    
    # Test can_trade
    allowed, reason = risk_mgr.can_trade(test_positions, 0.20)
    print(f"Can trade $0.20: {allowed} - {reason}")
    
    # Test position sizing
    market_price = 0.15
    estimated_prob = 0.35  # 35% true probability vs 15% market price
    bankroll = 10.00
    
    size = risk_mgr.calculate_position_size(market_price, estimated_prob, bankroll)
    print(f"\nPosition size for {estimated_prob*100:.1f}% edge at {market_price*100:.1f}% price: ${size:.4f}")
    
    # Test EV calculation
    ev_metrics = risk_mgr.calculate_expected_value(market_price, estimated_prob, size)
    print(f"\nExpected Value Metrics:")
    for key, value in ev_metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Test risk report
    risk_mgr.print_risk_report(test_positions, bankroll, bankroll)