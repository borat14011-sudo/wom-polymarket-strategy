# Risk Management Framework

> **Document Purpose:** Comprehensive risk framework for algorithmic trading systems, covering position sizing, correlations, circuit breakers, and drawdown controls.
> 
> **Version:** 1.0  
> **Last Updated:** 2026-02-08  
> **Owner:** Risk Modeling Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Position Sizing Models](#position-sizing-models)
3. [Correlation Matrices](#correlation-matrices)
4. [Circuit Breakers](#circuit-breakers)
5. [Maximum Drawdown Limits](#maximum-drawdown-limits)
6. [Integration & Monitoring](#integration--monitoring)
7. [Appendix: Code Examples](#appendix-code-examples)

---

## Executive Summary

This framework establishes risk controls for quantitative trading operations. All models operate in real-time with sub-second latency requirements.

### Risk Philosophy
- **Preserve capital first, profit second**
- **Position sizes scale inversely with volatility**
- **Correlations increase in crisis—plan accordingly**
- **Circuit breakers prevent catastrophic losses**

### Key Metrics Dashboard
| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| Daily VaR | < 2% | 2-5% | > 5% |
| Margin Utilization | < 50% | 50-75% | > 75% |
| Correlation Spike | < 0.3 | 0.3-0.7 | > 0.7 |
| Drawdown | < 5% | 5-15% | > 15% |

---

## Position Sizing Models

### 1. Kelly Criterion (Base Model)

The Kelly Criterion determines optimal position size based on win rate and payoff ratio.

```
Kelly % = (W × R - (1 - W)) / R

Where:
- W = Win probability (0-1)
- R = Average win / Average loss (payoff ratio)
```

**Implementation Note:** Use Half-Kelly or Quarter-Kelly for safety margin.

```python
def kelly_position(win_rate, payoff_ratio, account_value, fraction=0.5):
    """
    Calculate position size using Kelly Criterion with safety fraction.
    
    Args:
        win_rate: Probability of winning trade (0-1)
        payoff_ratio: Average win / average loss
        account_value: Current portfolio value
        fraction: Safety multiplier (0.25-0.5 recommended)
    """
    if payoff_ratio <= 0:
        return 0
    
    kelly_pct = (win_rate * payoff_ratio - (1 - win_rate)) / payoff_ratio
    kelly_pct = max(0, min(kelly_pct, 0.25))  # Cap at 25%
    
    return account_value * kelly_pct * fraction
```

### 2. Volatility Targeting (Primary Model)

Position sizes scale to maintain constant portfolio volatility.

```
Position Size = (Target Volatility / Asset Volatility) × Account Value × Signal Strength

Target Volatility: Typically 10-15% annualized
Asset Volatility: 20-day realized volatility
```

| Volatility Regime | Target Annual Vol | Leverage Limit |
|-------------------|-------------------|----------------|
| Low (<10%) | 12% | 2.0x |
| Normal (10-25%) | 12% | 1.5x |
| High (25-40%) | 10% | 1.0x |
| Extreme (>40%) | 8% | 0.5x |

```python
def volatility_targeted_position(
    current_price, 
    volatility_20d, 
    account_value,
    target_volatility=0.12,
    signal_strength=1.0
):
    """
    Calculate position size based on volatility targeting.
    """
    # Annualize daily volatility
    annual_vol = volatility_20d * np.sqrt(252)
    
    # Calculate target exposure
    vol_scalar = target_volatility / annual_vol
    
    # Apply leverage limits based on vol regime
    if annual_vol > 0.40:
        max_leverage = 0.5
    elif annual_vol > 0.25:
        max_leverage = 1.0
    elif annual_vol > 0.10:
        max_leverage = 1.5
    else:
        max_leverage = 2.0
    
    vol_scalar = min(vol_scalar, max_leverage)
    
    # Dollar exposure
    exposure = account_value * vol_scalar * signal_strength
    
    # Shares/contracts
    return exposure / current_price
```

### 3. Risk-Parity Sizing

Equal risk contribution across positions, not equal dollar amounts.

```python
def risk_parity_weights(returns_df, lookback=252, max_weight=0.15):
    """
    Calculate risk-parity weights for a portfolio.
    
    Args:
        returns_df: DataFrame of asset returns
        lookback: Days for covariance estimation
        max_weight: Maximum single position weight
    """
    # Calculate covariance matrix
    cov = returns_df.iloc[-lookback:].cov()
    
    # Inverse volatility weighting (simplified risk parity)
    inv_vol = 1 / returns_df.iloc[-lookback:].std()
    weights = inv_vol / inv_vol.sum()
    
    # Apply constraints
    weights = weights.clip(0, max_weight)
    weights = weights / weights.sum()  # Renormalize
    
    return weights
```

### 4. Maximum Position Limits

| Asset Class | Max Position | Max Portfolio % |
|-------------|--------------|-----------------|
| Single Equity | $5M | 10% |
| Single ETF | $10M | 15% |
| Single Crypto | $2M | 5% |
| Single Option | Delta $3M | 8% |
| Single Futures | Notional $20M | 20% |

---

## Correlation Matrices

### Real-Time Correlation Monitoring

Correlation breakdowns during market stress are primary sources of unexpected losses.

#### Rolling Correlation Calculation

```python
def calculate_rolling_correlations(returns_df, window=20):
    """
    Calculate rolling correlation matrix.
    
    Args:
        returns_df: DataFrame of asset returns (columns = assets)
        window: Rolling window in days
    
    Returns:
        Correlation matrix DataFrame
    """
    return returns_df.iloc[-window:].corr()


def correlation_spike_detection(
    current_corr, 
    baseline_corr, 
    threshold=0.3
):
    """
    Detect significant correlation regime changes.
    
    Returns:
        dict: Pairs with correlation increases above threshold
    """
    diff = current_corr - baseline_corr
    spikes = {}
    
    for i in range(len(diff.columns)):
        for j in range(i+1, len(diff.columns)):
            asset_i = diff.columns[i]
            asset_j = diff.columns[j]
            change = diff.iloc[i, j]
            
            if change > threshold:
                spikes[(asset_i, asset_j)] = {
                    'baseline': baseline_corr.iloc[i, j],
                    'current': current_corr.iloc[i, j],
                    'change': change
                }
    
    return spikes
```

### Stress Correlation Matrix

Expected correlations during market stress (use for stress testing):

```python
STRESS_CORRELATIONS = {
    # Asset Class Pairs -> Stress Correlation
    ('SPY', 'QQQ'): 0.95,      # US Large Cap - Tech
    ('SPY', 'IWM'): 0.90,      # Large - Small Cap
    ('SPY', 'EFA'): 0.85,      # US - Developed Intl
    ('SPY', 'EEM'): 0.80,      # US - Emerging
    ('SPY', 'TLT'): -0.40,     # Stocks - Bonds (weakens in crisis)
    ('SPY', 'GLD'): 0.20,      # Stocks - Gold (increases in crisis)
    ('SPY', 'VIX'): -0.85,     # Stocks - Volatility
    ('BTC', 'ETH'): 0.85,      # Crypto pair
    ('BTC', 'SPY'): 0.50,      # Crypto - Stocks (increases in risk-off)
    ('XLE', 'USO'): 0.80,      # Energy sector - Oil
    ('XLF', 'SPY'): 0.95,      # Financials - Market
}
```

### Correlation Risk Limits

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Avg Pair Correlation | > 0.4 | > 0.6 | Reduce position sizes 50% |
| Max Single Correlation | > 0.8 | > 0.95 | Close one leg |
| Correlation Dispersion | < 0.1 | — | Diversification breakdown |
| Cross-Asset Correlation | > 0.5 | > 0.7 | Reduce total exposure |

### Correlation-Adjusted Position Sizing

```python
def correlation_adjusted_sizing(
    base_position,
    correlations,
    portfolio_positions,
    max_correlation_exposure=2.0
):
    """
    Reduce position size based on portfolio correlation risk.
    
    Args:
        base_position: Unadjusted position size
        correlations: Correlation series vs existing positions
        portfolio_positions: Current position sizes
        max_correlation_exposure: Max combined correlated exposure
    """
    if len(portfolio_positions) == 0:
        return base_position
    
    # Calculate weighted average correlation with existing book
    corr_exposure = sum(
        abs(correlations.get(asset, 0)) * size 
        for asset, size in portfolio_positions.items()
    )
    
    # Scale down if adding this position would exceed limits
    total_exposure = corr_exposure + base_position
    
    if total_exposure > max_correlation_exposure:
        scale_factor = max_correlation_exposure / total_exposure
        return base_position * scale_factor
    
    return base_position
```

---

## Circuit Breakers

### Tiered Circuit Breaker System

Circuit breakers halt trading to prevent runaway losses.

#### Level 1: Position-Level Breakers

```python
POSITION_CIRCUIT_BREAKERS = {
    'max_single_trade_loss': 0.02,        # 2% of account per trade
    'max_intraday_position_loss': 0.05,   # 5% max loss on any position
    'max_overnight_gap_loss': 0.10,       # 10% gap down triggers review
    'max_slippage_pct': 0.01,             # 1% slippage halt
    'max_order_rejects': 5,               # After 5 rejects, halt strategy
}
```

#### Level 2: Strategy-Level Breakers

```python
STRATEGY_CIRCUIT_BREAKERS = {
    'daily_loss_limit': 0.03,             # 3% daily loss
    'weekly_loss_limit': 0.05,            # 5% weekly loss
    'monthly_loss_limit': 0.10,           # 10% monthly loss
    'consecutive_loss_days': 3,           # Halt after 3 losing days
    'win_rate_floor': 0.30,               # Halt if win rate < 30% (20+ trades)
    'max_drawdown_trigger': 0.15,         # Halt at 15% DD
    'volatility_spike': 3.0,              # Halt if VIX > 3x average
}
```

#### Level 3: Portfolio-Level Breakers

```python
PORTFOLIO_CIRCUIT_BREAKERS = {
    'portfolio_daily_loss': 0.05,         # 5% portfolio daily loss
    'portfolio_weekly_loss': 0.10,        # 10% portfolio weekly loss
    'margin_call_buffer': 0.10,           # Halt at 90% margin usage
    'liquidity_threshold': 0.20,          # Halt if >20% book is illiquid
    'correlation_regime_change': 0.30,    # Halt if avg correlation +30%
}
```

### Circuit Breaker Implementation

```python
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class BreakerLevel(Enum):
    GREEN = "green"      # Normal operation
    YELLOW = "yellow"    # Warning, reduce sizes
    RED = "red"          # Halt new positions
    BLACK = "black"      # Emergency unwind

@dataclass
class CircuitBreaker:
    name: str
    threshold: float
    current_value: float
    level: BreakerLevel
    triggered_at: datetime
    reset_after: timedelta
    
    def check(self, new_value: float) -> BreakerLevel:
        """Update and return current breaker state."""
        self.current_value = new_value
        
        # Check if should reset
        if self.triggered_at and datetime.now() > self.triggered_at + self.reset_after:
            self.level = BreakerLevel.GREEN
            self.triggered_at = None
        
        # Determine level
        if new_value >= self.threshold * 1.5:
            if self.level != BreakerLevel.BLACK:
                self.triggered_at = datetime.now()
            self.level = BreakerLevel.BLACK
        elif new_value >= self.threshold:
            if self.level != BreakerLevel.RED:
                self.triggered_at = datetime.now()
            self.level = BreakerLevel.RED
        elif new_value >= self.threshold * 0.7:
            self.level = BreakerLevel.YELLOW
        else:
            self.level = BreakerLevel.GREEN
        
        return self.level


class CircuitBreakerManager:
    def __init__(self):
        self.breakers = {
            'daily_pnl': CircuitBreaker(
                name='Daily PnL',
                threshold=-0.03,
                current_value=0.0,
                level=BreakerLevel.GREEN,
                triggered_at=None,
                reset_after=timedelta(hours=12)
            ),
            'drawdown': CircuitBreaker(
                name='Drawdown',
                threshold=-0.15,
                current_value=0.0,
                level=BreakerLevel.GREEN,
                triggered_at=None,
                reset_after=timedelta(days=1)
            ),
            'margin': CircuitBreaker(
                name='Margin Usage',
                threshold=0.90,
                current_value=0.0,
                level=BreakerLevel.GREEN,
                triggered_at=None,
                reset_after=timedelta(hours=1)
            ),
        }
        self.active_halts = set()
    
    def update(self, metrics: dict) -> dict:
        """Update all breakers with current metrics."""
        actions = {}
        
        for name, value in metrics.items():
            if name in self.breakers:
                level = self.breakers[name].check(value)
                
                if level == BreakerLevel.BLACK:
                    actions[name] = 'EMERGENCY_UNWIND'
                    self.active_halts.add(name)
                elif level == BreakerLevel.RED:
                    actions[name] = 'HALT_NEW_POSITIONS'
                    self.active_halts.add(name)
                elif level == BreakerLevel.YELLOW:
                    actions[name] = 'REDUCE_SIZE_50%'
                else:
                    if name in self.active_halts:
                        self.active_halts.discard(name)
                        actions[name] = 'RESUME'
        
        return actions
    
    def can_trade(self) -> bool:
        """Check if any breakers prevent new trades."""
        for name in self.active_halts:
            if self.breakers[name].level in [BreakerLevel.RED, BreakerLevel.BLACK]:
                return False
        return True
```

### Manual Override Procedures

| Scenario | Override Authority | Documentation Required |
|----------|-------------------|------------------------|
| Temporary Resume | Risk Manager | Incident report within 1hr |
| Threshold Adjustment | Head of Trading | Written justification |
| Complete Disable | CRO + CEO | Board notification required |

---

## Maximum Drawdown Limits

### Drawdown Definitions

```python
def calculate_drawdown(equity_curve):
    """
    Calculate drawdown statistics.
    
    Returns:
        dict with current_dd, max_dd, dd_duration, recovery_time
    """
    # Running maximum
    running_max = equity_curve.cummax()
    
    # Drawdown percentage
    drawdown = (equity_curve - running_max) / running_max
    
    # Current drawdown
    current_dd = drawdown.iloc[-1]
    
    # Maximum drawdown
    max_dd = drawdown.min()
    
    # Maximum drawdown duration
    in_drawdown = drawdown < 0
    dd_periods = []
    current_start = None
    
    for date, is_dd in in_drawdown.items():
        if is_dd and current_start is None:
            current_start = date
        elif not is_dd and current_start is not None:
            dd_periods.append((current_start, date))
            current_start = None
    
    max_duration = max(
        [(end - start).days for start, end in dd_periods],
        default=0
    )
    
    return {
        'current_drawdown': current_dd,
        'max_drawdown': max_dd,
        'max_dd_duration_days': max_duration,
        'drawdown_series': drawdown
    }
```

### Drawdown Limit Tiers

| Tier | Drawdown | Position Size | Action |
|------|----------|---------------|--------|
| Normal | < 5% | 100% | Normal trading |
| Caution | 5-10% | 75% | Reduce new positions |
| Warning | 10-15% | 50% | Mandatory size reduction |
| Critical | 15-20% | 25% | Halt non-essential strategies |
| Stop | > 20% | 0% | Full trading halt, review required |

### Dynamic Position Sizing Based on Drawdown

```python
def drawdown_adjusted_size(
    base_position_size,
    current_drawdown,
    max_drawdown_limit=0.20
):
    """
    Reduce position size based on current drawdown.
    Uses a cubic reduction curve for aggressive sizing reduction.
    """
    if current_drawdown >= max_drawdown_limit:
        return 0  # Full halt
    
    # Cubic reduction: gentle at first, aggressive near limit
    drawdown_ratio = current_drawdown / max_drawdown_limit
    reduction_factor = (1 - drawdown_ratio) ** 3
    
    return base_position_size * max(reduction_factor, 0)


def get_drawdown_tier(current_drawdown):
    """Return current drawdown tier and required actions."""
    tiers = [
        (0.00, 'NORMAL', 1.0, 'Continue normal trading'),
        (0.05, 'CAUTION', 0.75, 'Reduce new position sizes to 75%'),
        (0.10, 'WARNING', 0.50, 'Reduce to 50%, review strategies'),
        (0.15, 'CRITICAL', 0.25, 'Reduce to 25%, halt non-core'),
        (0.20, 'STOP', 0.0, 'Full trading halt, mandatory review'),
    ]
    
    for threshold, tier, size_pct, action in reversed(tiers):
        if current_drawdown >= threshold:
            return {
                'tier': tier,
                'size_multiplier': size_pct,
                'action': action
            }
    
    return tiers[0][1:]
```

### Drawdown Recovery Protocol

```
┌─────────────────────────────────────────────────────────┐
│               DRAWDOWN RECOVERY PROTOCOL                │
├─────────────────────────────────────────────────────────┤
│ 1. HALT: Stop all non-essential trading                 │
│ 2. ASSESS: Analyze cause (strategy, market, execution)  │
│ 3. RESIZE: Reduce all positions to 25% of normal        │
│ 4. TEST: Paper trade for 3 days minimum                 │
│ 5. RESTART: Gradually increase from 25% → 50% → 100%    │
│    - Each level requires 5 profitable days              │
│ 6. DOCUMENT: Full incident report to risk committee     │
└─────────────────────────────────────────────────────────┘
```

### Time-Based Drawdown Limits

| Timeframe | Hard Limit | Soft Limit |
|-----------|------------|------------|
| Intraday | 3% | 2% |
| Daily | 5% | 3% |
| Weekly | 8% | 5% |
| Monthly | 12% | 8% |
| Quarterly | 15% | 10% |
| Yearly | 20% | 15% |

---

## Integration & Monitoring

### Risk Dashboard Metrics

Real-time monitoring should track:

```python
RISK_DASHBOARD_METRICS = {
    # PnL Metrics
    'daily_pnl_pct': 'Current day P&L %',
    'realized_pnl_mtd': 'Month-to-date realized',
    'unrealized_pnl': 'Current unrealized P&L',
    
    # Position Metrics
    'gross_exposure': 'Total long + short exposure',
    'net_exposure': 'Net market exposure',
    'margin_utilization': 'Current margin usage %',
    'concentration_risk': 'Largest position %',
    
    # Risk Metrics
    'portfolio_var_95': '95% VaR (1-day)',
    'portfolio_var_99': '99% VaR (1-day)',
    'expected_shortfall': 'Expected shortfall (CVaR)',
    'current_drawdown': 'Drawdown from peak',
    'max_drawdown_1yr': 'Maximum drawdown (1 year)',
    
    # Correlation Metrics
    'avg_correlation': 'Average pairwise correlation',
    'correlation_dispersion': 'Std dev of correlations',
    'beta_to_spy': 'Portfolio beta to S&P 500',
    
    # Circuit Breakers
    'breaker_status': 'Active circuit breakers',
    'days_since_last_trigger': 'Time since last halt',
}
```

### Risk Reporting Schedule

| Report | Frequency | Recipients | Latency |
|--------|-----------|------------|---------|
| Position Report | Real-time | Trading desk | < 1s |
| Risk Dashboard | Real-time | Risk team | < 5s |
| P&L Attribution | End of day | Portfolio managers | EOD |
| Risk Summary | Daily | Senior management | Next morning |
| Stress Test | Weekly | Risk committee | Weekly |
| Full Risk Report | Monthly | Board | Monthly |

### Alert Escalation Matrix

| Alert Type | Level 1 | Level 2 | Level 3 |
|------------|---------|---------|---------|
| Position limit breach | Trader | Risk Manager | Head of Trading |
| Daily loss > 2% | Risk Manager | Head of Trading | CRO |
| Daily loss > 5% | Head of Trading | CRO | CEO |
| Circuit breaker trigger | Risk Manager | CRO | Board Chair |
| Drawdown > 10% | Head of Trading | CRO | CEO |
| Drawdown > 15% | CRO | CEO | Board Chair |

---

## Appendix: Code Examples

### Complete Risk Manager Class

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

class RiskManager:
    """
    Comprehensive risk management for trading systems.
    """
    
    def __init__(
        self,
        account_value: float,
        max_position_pct: float = 0.10,
        max_portfolio_var: float = 0.02,
        target_volatility: float = 0.15
    ):
        self.account_value = account_value
        self.max_position_pct = max_position_pct
        self.max_portfolio_var = max_portfolio_var
        self.target_volatility = target_volatility
        
        self.positions = {}
        self.equity_curve = []
        self.circuit_breakers = CircuitBreakerManager()
        
    def calculate_position_size(
        self,
        symbol: str,
        signal_strength: float,
        volatility: float,
        correlation_with_book: Optional[float] = None
    ) -> Dict:
        """
        Calculate risk-adjusted position size.
        """
        # Check circuit breakers
        if not self.circuit_breakers.can_trade():
            return {'size': 0, 'reason': 'Circuit breaker active'}
        
        # Base size from volatility targeting
        vol_scalar = self.target_volatility / (volatility * np.sqrt(252))
        base_size = self.account_value * vol_scalar * signal_strength
        
        # Apply position limit
        max_position = self.account_value * self.max_position_pct
        size = min(base_size, max_position)
        
        # Apply correlation adjustment
        if correlation_with_book and correlation_with_book > 0.5:
            size *= (1 - correlation_with_book)
        
        # Apply drawdown adjustment
        current_dd = self.get_current_drawdown()
        size = drawdown_adjusted_size(size, current_dd)
        
        # Final checks
        if size < 1000:  # Minimum position size
            return {'size': 0, 'reason': 'Below minimum size'}
        
        return {
            'size': size,
            'shares': int(size / self.get_price(symbol)),
            'risk_factor': vol_scalar,
            'drawdown_factor': drawdown_adjusted_size(1, current_dd)
        }
    
    def update(self, timestamp: datetime, pnl: float, positions: Dict):
        """Update risk state with latest data."""
        self.account_value += pnl
        self.equity_curve.append((timestamp, self.account_value))
        self.positions = positions
        
        # Calculate metrics
        metrics = self.calculate_metrics()
        
        # Check circuit breakers
        actions = self.circuit_breakers.update({
            'daily_pnl': pnl / self.account_value,
            'drawdown': self.get_current_drawdown(),
            'margin': metrics['margin_utilization']
        })
        
        return metrics, actions
    
    def calculate_metrics(self) -> Dict:
        """Calculate current risk metrics."""
        if len(self.equity_curve) < 2:
            return {}
        
        equity_series = pd.Series(
            [e[1] for e in self.equity_curve],
            index=[e[0] for e in self.equity_curve]
        )
        
        dd_stats = calculate_drawdown(equity_series)
        
        return {
            'account_value': self.account_value,
            'current_drawdown': dd_stats['current_drawdown'],
            'max_drawdown': dd_stats['max_drawdown'],
            'margin_utilization': self.calculate_margin(),
            'gross_exposure': sum(abs(p) for p in self.positions.values()),
            'net_exposure': sum(self.positions.values()),
        }
    
    def get_current_drawdown(self) -> float:
        """Get current drawdown percentage."""
        if not self.equity_curve:
            return 0.0
        
        peak = max(e[1] for e in self.equity_curve)
        current = self.equity_curve[-1][1]
        
        return (current - peak) / peak if peak > 0 else 0
    
    def get_price(self, symbol: str) -> float:
        """Get current price for symbol (placeholder)."""
        return 100.0  # Implement actual price feed
    
    def calculate_margin(self) -> float:
        """Calculate margin utilization (placeholder)."""
        return 0.5  # Implement actual margin calc


# Example usage
if __name__ == "__main__":
    risk_mgr = RiskManager(
        account_value=1_000_000,
        max_position_pct=0.10,
        target_volatility=0.15
    )
    
    # Calculate position size
    result = risk_mgr.calculate_position_size(
        symbol='AAPL',
        signal_strength=1.0,
        volatility=0.25
    )
    
    print(f"Position size: ${result.get('size', 0):,.2f}")
    print(f"Shares: {result.get('shares', 0)}")
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-08 | RISK_MODELER_1 | Initial framework |

### Review Schedule

- **Monthly:** Circuit breaker thresholds and limits
- **Quarterly:** Full framework review
- **Annually:** Comprehensive stress testing and validation

---

*This framework is a living document. All traders and risk personnel must review and acknowledge updates within 48 hours of publication.*
